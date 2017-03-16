#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

import re
from sys import exc_info, stdout
from textwrap import wrap
import logging
import pickle

import six
from six.moves import xrange

try:
    from yaml import dump
except ImportError:
    #dump = lambda x,**y: str(x)
    # YAML uses lowercase True/False
    def dump(x, **args):
        if type(x) is bool:
            return str(x).lower()
        return str(x)


try:
    import argparse
    argparse_is_available = True
except ImportError:
    argparse_is_available = False

__all__ = ('ConfigBlock', 'ConfigList', 'ConfigValue')

logger = logging.getLogger('pyutilib.misc')


def _munge_name(name, space_to_dash=True):
    if space_to_dash:
        name = re.sub(r'\s', '-', name)
    name = re.sub(r'_', '-', name)
    return re.sub(r'[^a-zA-Z0-9-_]', '_', name)


_leadingSpace = re.compile('^([ \n\t]*)')


def _strip_indentation(doc):
    if not doc:
        return doc
    lines = doc.splitlines()
    if len(lines) == 1:
        return doc.lstrip()
    minIndent = min(len(_leadingSpace.match(l).group(0)) for l in lines[1:])
    if len(_leadingSpace.match(lines[0]).group(0)) <= minIndent:
        lines[0] = lines[0].strip()
    else:
        lines[0] = lines[0][minIndent:].rstrip()
    for i, l in enumerate(lines[1:]):
        lines[i + 1] = l[minIndent:].rstrip()
    return '\n'.join(lines)


class _UnpickleableDomain(object):
    def __init__(self, obj):
        self._type = type(obj).__name__
        self._name = obj.name(True)

    def __call__(self, arg):
        logging.error(
"""%s %s was pickled with an unpicklable domain.
    The domain was stripped and lost during the pickle process.  Setting
    new values on the restored object cannot be mapped into the correct
    domain.
""" % ( self._type, self._name))
        return arg

def _picklable(field,obj):
    try:
        pickle.dumps(field)
        return field
    except:
        # Contrary to the documentation, Python is not at all consistent
        # with the exception that is raised when pickling an object
        # fails:
        #
        #    Python 2.6 - 3.4:  pickle.PicklingError
        #    Python 3.5 - 4.6:  AttributeError
        #    Python 2.6 - 2.7 (cPickle):  TypeError
        #
        # What we are concerned about is masking things like recursion
        # errors.  Unfortunately, Python is not quite consistent there,
        # either: exceeding recursion depth raises a RuntimeError
        # through 3.4, then switches to a RecursionError (a derivative
        # of RuntimeError).
        if isinstance(exc_info()[0], RuntimeError):
            raise
        return _UnpickleableDomain(obj)


class ConfigBase(object):
    __slots__ = ('_parent', '_name', '_userSet', '_userAccessed', '_data',
                 '_default', '_domain', '_description', '_doc', '_visibility',
                 '_argparse')

    # This just needs to be any reference-counted object; we use it so
    # that we can tell if an argument is provided (and we can't use None
    # as None is a valid user-specified argument)
    NoArgument = (None,)

    def __init__(self,
                 default=None,
                 domain=None,
                 description=None,
                 doc=None,
                 visibility=0):
        self._parent = None
        self._name = None
        self._userSet = False
        self._userAccessed = False

        self._data = None
        self._default = default
        self._domain = domain
        self._description = _strip_indentation(description)
        self._doc = _strip_indentation(doc)
        self._visibility = visibility
        self._argparse = None

    def __getstate__(self):
        # Nominally, __getstate__() should return:
        #
        # state = super(Class, self).__getstate__()
        # for i in Class.__slots__:
        #    state[i] = getattr(self,i)
        # return state
        #
        # Hoewever, in this case, the (nominal) parent class is
        # 'object', and object does not implement __getstate__.  Since
        # super() doesn't actually return a class, we are going to check
        # the *derived class*'s MRO and see if this is the second to
        # last class (the last is always 'object').  If it is, then we
        # can allocate the state dictionary.  If it is not, then we call
        # the super-class's __getstate__ (since that class is NOT
        # 'object').
        if self.__class__.__mro__[-2] is ConfigBase:
            state = {}
        else:
            state = super(ConfigBase, self).__getstate__()
        state.update((key, getattr(self, key)) for key in ConfigBase.__slots__)
        state['_domain'] = _picklable(state['_domain'], self)
        state['_parent'] = None
        return state

    def __setstate__(self, state):
        for key, val in six.iteritems(state):
            # Note: per the Python data model docs, we explicitly
            # set the attribute using object.__setattr__() instead
            # of setting self.__dict__[key] = val.
            object.__setattr__(self, key, val)

    def __call__(self, value=NoArgument):
        ans = self.__class__()
        ans._default     = self._default
        ans._domain      = self._domain
        ans._description = self._description
        ans._doc         = self._doc
        ans._visibility  = self._visibility
        if self.__class__ is ConfigBlock:
            ans._implicit_declaration = self._implicit_declaration
            ans._implicit_domain = self._implicit_domain
            for k in self._decl_order:
                if k in self._declared:
                    v = self._data[k]
                    ans._data[k] = _tmp = v()
                    ans._decl_order.append(k)
                    ans._declared.add(k)
                    _tmp._parent = ans
                    _tmp._name = v._name
        else:
            ans.reset()
        if value is not ConfigBase.NoArgument:
            ans.set_value(value)
        return ans

    def name(self, fully_qualified=False):
        # Special case for the top-level block
        if self._name is None:
            return ""
        elif fully_qualified and self._parent is not None:
            pName = self._parent.name(fully_qualified)
            # Special case for ConfigList indexing and the top-level entries
            if self._name.startswith('[') or not pName:
                return pName + self._name
            else:
                return pName + '.' + self._name
        else:
            return self._name

    def _cast(self, value):
        if value is None:
            return value
        if self._domain is not None:
            try:
                return self._domain(value)
            except:
                err = exc_info()[1]
                if hasattr(self._domain, '__name__'):
                    _dom = self._domain.__name__
                else:
                    _dom = type(self._domain)
                raise ValueError("invalid value for configuration '%s':\n"
                                 "\tFailed casting %s\n\tto %s\n\tError: %s" %
                                 (self.name(True), value, _dom, err))
        else:
            return value

    def reset(self):
        #
        # This is a dangerous construct, the failure in the first try block
        # can mask a real problem.
        #
        try:
            self.set_value(self._default)
        except:
            if hasattr(self._default, '__call__'):
                self.set_value(self._default())
            else:
                raise
        self._userAccessed = False
        self._userSet = False

    def declare_as_argument(self, *args, **kwds):
        """Map this Config item to an argparse argument.

Valid arguments include all valid arguments to argparse's
ArgumentParser.add_argument() with the exception of 'default'.  In addition,
you may provide a group keyword argument can be used to either pass in a
pre-defined option group or subparser, or else pass in the title of a
group, subparser, or (subparser, group)."""

        if 'default' in kwds:
            raise TypeError(
                "You cannot specify an argparse default value with "
                "ConfigBase.declare_as_argument().  The default value is "
                "supplied automatically from the Config definition.")

        if 'action' not in kwds and self._domain is bool:
            if not self._default:
                kwds['action'] = 'store_true'
            else:
                kwds['action'] = 'store_false'
                if not args:
                    args = ('--disable-' + _munge_name(self.name()),)
                if 'help' not in kwds:
                    kwds['help'] = "[DON'T] " + self._description
        if 'help' not in kwds:
            kwds['help'] = self._description
        if not args:
            args = ('--' + _munge_name(self.name()),)
        if self._argparse:
            self._argparse = self._argparse + ((args, kwds),)
        else:
            self._argparse = ((args, kwds),)
        return self

    def initialize_argparse(self, parser):

        def _get_subparser_or_group(_parser, name):
            # Note: strings also have a 'title()' method.  We are
            # looking for things that look like argparse
            # groups/subparsers, so just checking for the attribute
            # is insufficient: it needs to be a string attribute as
            # well
            if isinstance(name, argparse._ActionsContainer):
                #hasattr(_group, 'title') and \
                #    isinstance(_group.title, six.string_types):
                return 2, name

            if not isinstance(name, six.string_types):
                raise RuntimeError(
                    'Unknown datatype (%s) for argparse group on '
                    'configuration definition %s' %
                    (type(name).__name__, obj.name(True)))

            try:
                for _grp in _parser._subparsers._group_actions:
                    if name in _grp._name_parser_map:
                        return 1, _grp._name_parser_map[name]
            except AttributeError:
                pass

            for _grp in _parser._action_groups:
                if _grp.title == name:
                    return 0, _grp
            return 0, _parser.add_argument_group(title=name)

        def _process_argparse_def(_args, _kwds):
            _parser = parser
            # shallow copy the dict so we can remove the group flag and
            # add things like documentation, etc.
            _kwds = dict(_kwds)
            if 'group' in _kwds:
                _group = _kwds.pop('group')
                if isinstance(_group, tuple):
                    for _idx, _grp in enumerate(_group):
                        _issub, _parser = _get_subparser_or_group(_parser, _grp)
                        if not _issub and _idx < len(_group) - 1:
                            raise RuntimeError(
                                "Could not find argparse subparser '%s' for "
                                "Config item %s" % (_grp, obj.name(True)))
                else:
                    _issub, _parser = _get_subparser_or_group(_parser, _group)
            if 'dest' not in _kwds:
                _kwds['dest'] = 'CONFIGBLOCK.' + obj.name(True)
                if 'metavar' not in _kwds and \
                   _kwds.get('action','') not in ('store_true','store_false'):
                    if obj._domain is not None and \
                       obj._domain.__class__ is type:
                        _kwds['metavar'] = obj._domain.__name__.upper()
                    else:
                        _kwds['metavar'] = _munge_name(self.name().upper(),
                                                       False)
            _parser.add_argument(*_args, default=argparse.SUPPRESS, **_kwds)

        assert (argparse_is_available)
        for level, value, obj in self._data_collector(None, ""):
            if obj._argparse is None:
                continue
            for _args, _kwds in obj._argparse:
                _process_argparse_def(_args, _kwds)

    def import_argparse(self, parsed_args):
        for level, value, obj in self._data_collector(None, ""):
            if obj._argparse is None:
                continue
            for _args, _kwds in obj._argparse:
                if 'dest' in _kwds:
                    _dest = _kwds['dest']
                    if _dest in parsed_args:
                        obj.set_value(parsed_args.__dict__[_dest])
                else:
                    _dest = 'CONFIGBLOCK.' + obj.name(True)
                    if _dest in parsed_args:
                        obj.set_value(parsed_args.__dict__[_dest])
                        del parsed_args.__dict__[_dest]
        return parsed_args

    def display(self, content_filter=None, indent_spacing=2, ostream=None):
        if content_filter not in ConfigBlock.content_filters:
            raise ValueError("unknown content filter '%s'; valid values are %s"
                             % (content_filter, ConfigBlock.content_filters))

        _blocks = []
        if ostream is None:
            ostream=stdout

        for level, value, obj in self._data_collector(0, ""):
            if content_filter == 'userdata' and not obj._userSet:
                continue

            _blocks[level:] = [' ' * indent_spacing * level + value + "\n",]

            for i, v in enumerate(_blocks):
                if v is not None:
                    ostream.write(v)
                    _blocks[i] = None

    def generate_yaml_template(self, indent_spacing=2, width=78, visibility=0):
        minDocWidth = 20
        comment = "  # "
        data = list(self._data_collector(0, "", visibility))
        level_info = {}
        for lvl, val, obj in data:
            if lvl not in level_info:
                level_info[lvl] = {'data': [], 'off': 0, 'line': 0, 'over': 0}
            level_info[lvl]['data'].append(
                (val.find(':') + 2, len(val), len(obj._description or "")))
        for lvl in sorted(level_info):
            indent = lvl * indent_spacing
            _ok = width - indent - len(comment) - minDocWidth
            offset = \
                max( val if val < _ok else key
                     for key,val,doc in level_info[lvl]['data'] )
            offset += indent + len(comment)
            over = sum(1 for key, val, doc in level_info[lvl]['data']
                       if doc + offset > width)
            if len(level_info[lvl]['data']) - over > 0:
                line = max(offset + doc
                           for key, val, doc in level_info[lvl]['data']
                           if offset + doc <= width)
            else:
                line = width
            level_info[lvl]['off'] = offset
            level_info[lvl]['line'] = line
            level_info[lvl]['over'] = over
        maxLvl = 0
        maxDoc = 0
        pad = 0
        for lvl in sorted(level_info):
            _pad = level_info[lvl]['off']
            _doc = level_info[lvl]['line'] - _pad
            if _pad > pad:
                if maxDoc + _pad <= width:
                    pad = _pad
                else:
                    break
            if _doc + pad > width:
                break
            if _doc > maxDoc:
                maxDoc = _doc
            maxLvl = lvl
        os = six.StringIO()
        if self._description:
            os.write(comment.lstrip() + self._description + "\n")
        for lvl, val, obj in data:
            if not obj._description:
                os.write(' ' * indent_spacing * lvl + val + "\n")
                continue
            if lvl <= maxLvl:
                field = pad - len(comment)
            else:
                field = level_info[lvl]['off'] - len(comment)
            os.write(' ' * indent_spacing * lvl)
            if width - len(val) - minDocWidth >= 0:
                os.write('%%-%ds' % (field - indent_spacing * lvl) % val)
            else:
                os.write(val + '\n' + ' ' * field)
            os.write(comment)
            txtArea = max(width - field - len(comment), minDocWidth)
            os.write(("\n" + ' ' * field + comment).join(
                wrap(
                    obj._description, txtArea, subsequent_indent='  ')))
            os.write('\n')
        return os.getvalue()

    def generate_documentation\
            ( self,
              block_start= "\\begin{description}[topsep=0pt,parsep=0.5em,itemsep=-0.4em]\n",
              block_end=   "\\end{description}\n",
              item_start=  "\\item[{%s}]\\hfill\n",
              item_body=   "\\\\%s",
              item_end=    "",
              indent_spacing=2,
              width=78,
              visibility=0
              ):
        os = six.StringIO()
        level = []
        lastObj = self
        indent = ''
        for lvl, val, obj in self._data_collector(1, '', visibility, True):
            #print len(level), lvl, val, obj
            if len(level) < lvl:
                while len(level) < lvl - 1:
                    level.append(None)
                level.append(lastObj)
                if '%s' in block_start:
                    os.write(indent + block_start % lastObj.name())
                elif block_start:
                    os.write(indent + block_start)
                indent += ' ' * indent_spacing
            while len(level) > lvl:
                _last = level.pop()
                if _last is not None:
                    indent = indent[:-1 * indent_spacing]
                    if '%s' in block_end:
                        os.write(indent + block_end % _last.name())
                    elif block_end:
                        os.write(indent + block_end)

            lastObj = obj
            if '%s' in item_start:
                os.write(indent + item_start % obj.name())
            elif item_start:
                os.write(indent + item_start)
            _doc = obj._doc or obj._description or ""
            if _doc:
                _wrapLines = '\n ' not in _doc
                if '%s' in item_body:
                    _doc = item_body % (_doc,)
                elif _doc:
                    _doc = item_body
                if _wrapLines:
                    doc_lines = wrap(
                        _doc,
                        width,
                        initial_indent=indent + ' ' * indent_spacing,
                        subsequent_indent=indent + ' ' * indent_spacing)
                else:
                    doc_lines = (_doc,)
                # Write things out
                os.writelines('\n'.join(doc_lines))
                if not doc_lines[-1].endswith("\n"):
                    os.write('\n')
            if '%s' in item_end:
                os.write(indent + item_end % obj.name())
            elif item_end:
                os.write(indent + item_end)
        while level:
            indent = indent[:-1 * indent_spacing]
            _last = level.pop()
            if '%s' in block_end:
                os.write(indent + block_end % _last.name())
            else:
                os.write(indent + block_end)
        return os.getvalue()

    def user_values(self):
        if self._userSet:
            yield self
        for level, value, obj in self._data_collector(0, ""):
            if obj._userSet:
                yield obj

    def unused_user_values(self):
        if self._userSet and not self._userAccessed:
            yield self
        for level, value, obj in self._data_collector(0, ""):
            if obj._userSet and not obj._userAccessed:
                yield obj


class ConfigValue(ConfigBase):

    def __init__(self, *args, **kwds):
        ConfigBase.__init__(self, *args, **kwds)
        self.reset()

    def value(self, accessValue=True):
        if accessValue:
            self._userAccessed = True
        return self._data

    def set_value(self, value):
        self._data = self._cast(value)
        self._userSet = True

    def _data_collector(self, level, prefix, visibility=None, docMode=False):
        if visibility is not None and visibility < self._visibility:
            return
        _str = dump(self._data, default_flow_style=True).rstrip()
        if _str.endswith("..."):
            _str = _str[:-3].rstrip()
        yield (level, prefix + _str, self)


class ConfigList(ConfigBase):

    def __init__(self, *args, **kwds):
        ConfigBase.__init__(self, *args, **kwds)
        if self._domain is None:
            self._domain = ConfigValue()
        elif isinstance(self._domain, ConfigBase):
            pass
        else:
            self._domain = ConfigValue(None, domain=self._domain)
        self.reset()


    def __setstate__(self, state):
        state = super(ConfigList, self).__setstate__(state)
        for x in self._data:
            x._parent = self

    def __getitem__(self, key):
        val = self._data[key]
        self._userAccessed = True
        if isinstance(val, ConfigValue):
            return val.value()
        else:
            return val

    def get(self, key, default=ConfigBase.NoArgument):
        # Note: get() is borrowed from ConfigBlock for cases where we
        # want the raw stored object (and to aviod the implicit
        # conversion of ConfigValue members to their stored data).
        try:
            val = self._data[key]
            self._userAccessed = True
            return val
        except:
            pass
        if default is ConfigBase.NoArgument:
            return None
        if self._domain is not None:
            return self._domain(default)
        else:
            return ConfigValue(default)

    def __setitem__(self, key, val):
        # Note: this will fail if the element doesn't exist in _data.
        # As a result, *this* list doesn't change when someone tries to
        # change an element; instead, the *element* gets its _userSet
        # flag set.
        #self._userSet = True
        self._data[key].set_value(val)

    def __len__(self):
        return self._data.__len__()

    def __iter__(self):
        self._userAccessed = True
        return iter(self[i] for i in xrange(len(self._data)))

    def value(self, accessValue=True):
        if accessValue:
            self._userAccessed = True
        return [config.value(accessValue) for config in self._data]

    def set_value(self, value):
        # If the set_value fails part-way through the list values, we
        # want to restore a deterministic state.  That is, either
        # set_value succeeds completely, or else nothing happens.
        _old = self._data
        self._data = []
        try:
            if (type(value) is list) or \
               isinstance(value, ConfigList):
                for val in value:
                    self.append(val)
            else:
                self.append(value)
        except:
            self._data = _old
            raise
        self._userSet = True

    def reset(self):
        ConfigBase.reset(self)
        # Because the base reset() calls set_value, any deefault list
        # entries will get their userSet flag set.  This is wrong, as
        # reset() should conceptually reset teh object to it's default
        # state (e.g., before the user ever had a chance to mess with
        # things).  As the list could contain a ConfigBlock, this is a
        # recursive operation to put the userSet values back.
        for val in self.user_values():
            val._userSet = False

    def append(self, value=ConfigBase.NoArgument):
        val = self._cast(value)
        if val is None:
            return
        self._data.append(val)
        #print self._data[-1], type(self._data[-1])
        self._data[-1]._parent = self
        self._data[-1]._name = '[%s]' % (len(self._data) - 1,)
        self._data[-1]._userSet = True
        self._userSet = True

    def add(self, value=ConfigBase.NoArgument):
        logger.warning(
            "DEPRECATED: ConfigList.add() has been deprecated.  Use append()")
        return self.append(value)

    def _data_collector(self, level, prefix, visibility=None, docMode=False):
        if visibility is not None and visibility < self._visibility:
            return
        if docMode:
            # In documentation mode, we do NOT list the documentation
            # for any sub-data, and instead document the *domain*
            # information (as all the entries should share the same
            # domain, potentially duplicating that documentation is
            # somewhat redundant, and worse, if the list is empty, then
            # no documentation is generated at all!)
            yield (level, prefix.rstrip(), self)
            subDomain = self._domain._data_collector(level + 1, '- ',
                                                     visibility, docMode)
            # Pop off the (empty) block entry
            six.next(subDomain)
            for v in subDomain:
                yield v
            return
        if prefix:
            if not self._data:
                yield (level, prefix.rstrip() + ' []', self)
            else:
                yield (level, prefix.rstrip(), self)
                if level is not None:
                    level += 1
        for value in self._data:
            for v in value._data_collector(level, '- ', visibility, docMode):
                yield v


class ConfigBlock(ConfigBase):
    content_filters = (None, 'all', 'userdata')

    __slots__ = ('_decl_order', '_declared', '_implicit_declaration',
                 '_implicit_domain')
    _all_slots = __slots__ + ConfigBase.__slots__

    def __init__(self,
                 description=None,
                 doc=None,
                 implicit=False,
                 implicit_domain=None,
                 visibility=0):
        self._decl_order = []
        self._declared = set()
        self._implicit_declaration = implicit
        if implicit_domain is None or isinstance(implicit_domain, ConfigBase):
            self._implicit_domain = implicit_domain
        else:
            self._implicit_domain = ConfigValue(None, domain=implicit_domain)
        ConfigBase.__init__(self, None, {}, description, doc, visibility)
        self._data = {}

    def __getstate__(self):
        state = super(ConfigBlock, self).__getstate__()
        state.update((key, getattr(self, key)) for key in ConfigBlock.__slots__)
        state['_implicit_domain'] = _picklable(state['_implicit_domain'], self)
        return state

    def __setstate__(self, state):
        state = super(ConfigBlock, self).__setstate__(state)
        for x in six.itervalues(self._data):
            x._parent = self

    def __getitem__(self, key):
        self._userAccessed = True
        key = str(key)
        if isinstance(self._data[key], ConfigValue):
            return self._data[key].value()
        else:
            return self._data[key]

    def get(self, key, default=ConfigBase.NoArgument):
        self._userAccessed = True
        key = str(key)
        if key in self._data:
            return self._data[key]
        if default is ConfigBase.NoArgument:
            return None
        if self._implicit_domain is not None:
            return self._implicit_domain(default)
        else:
            return ConfigValue(default)

    def setdefault(self, key, default=ConfigBase.NoArgument):
        self._userAccessed = True
        key = str(key)
        if key in self._data:
            return self._data[key]
        if default is ConfigBase.NoArgument:
            return self.add(key, None)
        else:
            return self.add(key, default)

    def __setitem__(self, key, val):
        key = str(key)
        if key not in self._data:
            self.add(key, val)
        else:
            self._data[key].set_value(val)
        #self._userAccessed = True

    def __contains__(self, key):
        key = str(key)
        return key in self._data

    def __len__(self):
        return self._decl_order.__len__()

    def __iter__(self):
        return self._decl_order.__iter__()

    def __getattr__(self, name):
        # Note: __getattr__ is only called after all "usual" attribute
        # lookup methods have failed.  So, if we get here, we already
        # know that key is not a __slot__ or a method, etc...
        #if name in ConfigBlock._all_slots:
        #    return super(ConfigBlock,self).__getattribute__(name)
        if name not in self._data:
            _name = name.replace('_', ' ')
            if _name not in self._data:
                raise AttributeError("Unknown attribute '%s'" % name)
            name = _name
        return ConfigBlock.__getitem__(self, name)

    def __setattr__(self, name, value):
        if name in ConfigBlock._all_slots:
            super(ConfigBlock, self).__setattr__(name, value)
        else:
            if name not in self._data:
                name = name.replace('_', ' ')
            ConfigBlock.__setitem__(self, name, value)

    def iterkeys(self):
        return self._decl_order.__iter__()

    def itervalues(self):
        self._userAccessed = True
        for key in self._decl_order:
            yield self[key]

    def iteritems(self):
        self._userAccessed = True
        for key in self._decl_order:
            yield (key, self[key])

    def keys(self):
        return list(self.iterkeys())

    def values(self):
        return list(self.itervalues())

    def items(self):
        return list(self.iteritems())

    def _add(self, name, config):
        name = str(name)
        if config._parent is not None:
            raise ValueError(
                "config '%s' is already assigned to Config Block '%s'; "
                "cannot reassign to '%s'" %
                (name, config._parent.name(True), self.name(True)))
        if name in self._data:
            raise ValueError(
                "duplicate config '%s' defined for Config Block '%s'" %
                (name, self.name(True)))
        if '.' in name or '[' in name or ']' in name:
            raise ValueError(
                "Illegal character in config '%s' for config Block '%s': "
                "'.[]' are not allowed." % (name, self.name(True)))
        self._data[name] = config
        self._decl_order.append(name)
        config._parent = self
        config._name = name
        return config

    def declare(self, name, config):
        ans = self._add(name, config)
        self._declared.add(name)
        return ans

    def add(self, name, config):
        if not self._implicit_declaration:
            raise ValueError("Key '%s' not defined in Config Block '%s'"
                             " and Block disallows implicit entries" %
                             (name, self.name(True)))

        if self._implicit_domain is None:
            if isinstance(config, ConfigBase):
                ans = self._add(name, config)
            else:
                ans = self._add(name, ConfigValue(config))
        else:
            ans = self._add(name, self._implicit_domain(config))
        self._userSet = True
        return ans

    def value(self, accessValue=True):
        if accessValue:
            self._userAccessed = True
        return dict((name, config.value(accessValue))
                    for name, config in six.iteritems(self._data))

    def set_value(self, value):
        if value is None:
            return
        if (type(value) is not dict) and \
           (not isinstance(value, ConfigBlock)):
            raise ValueError("Expected dict value for %s.set_value, found %s" %
                             (self.name(True), type(value).__name__))
        _implicit = []
        _decl_map = {}
        for key in value:
            if str(key) in self._data:
                # str(key) may not be key... store the mapping so that
                # when we later iterate over the _decl_order, we can map
                # the local keys back to the incoming value keys.
                _decl_map[str(key)] = key
            else:
                if self._implicit_declaration:
                    _implicit.append(key)
                else:
                    raise ValueError(
                        "key '%s' not defined for Config Block '%s' and "
                        "implicit (undefined) keys are not allowed" %
                        (key, self.name(True)))

        # If the set_value fails part-way through the new values, we
        # want to restore a deterministic state.  That is, either
        # set_value succeeds completely, or else nothing happens.
        _old_data = self.value(False)
        try:
            # We want to set the values in declaration order (so that
            # things are deterministic and in case a validation depends
            # on the order)
            for key in self._decl_order:
                if key in _decl_map:
                    #print "Setting", key, " = ", value
                    self._data[key].set_value(value[_decl_map[key]])
            # implicit data is declated at the end (in sorted order)
            for key in sorted(_implicit):
                self.add(key, value[key])
        except:
            self.reset()
            self.set_value(_old_data)
            raise
        self._userSet = True

    def reset(self):
        # Reset the values in the order they were declared.  This
        # allows reset functions to have a deterministic ordering.
        def _keep(self, key):
            keep = key in self._declared
            if keep:
                self._data[key].reset()
            else:
                del self._data[key]
            return keep
        # this is an in-place slice of a list...
        self._decl_order[:] = [x for x in self._decl_order if _keep(self, x)]
        self._userAccessed = False
        self._userSet = False

    def _data_collector(self, level, prefix, visibility=None, docMode=False):
        if visibility is not None and visibility < self._visibility:
            return
        if prefix:
            yield (level, prefix.rstrip(), self)
            if level is not None:
                level += 1
        for key in self._decl_order:
            for v in self._data[key]._data_collector(level, key + ': ',
                                                     visibility, docMode):
                yield v

# In Python3, the items(), etc methods of dict-like things return
# generator-like objects.
if six.PY3:
    ConfigBlock.keys = ConfigBlock.iterkeys
    ConfigBlock.values = ConfigBlock.itervalues
    ConfigBlock.items = ConfigBlock.iteritems
