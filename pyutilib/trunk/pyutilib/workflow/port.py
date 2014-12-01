#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

__all__ = ['Port', 'Ports', 'InputPorts', 'OutputPorts']

import weakref

from pyutilib.workflow.connector import DirectConnector

import pprint

def define_connection(cls, from_port, to_port):
    """Define a connection by constructing the specified class."""
    # TODO: Generate a warning if required input is connect to an optional output

    #
    # Raise an exception if the port action is store and there already exists a connection.
    #
    if to_port.action == 'store' and len(to_port.input_connections) == 1:
        raise ValueError("Cannot connect to task %s port %s from task %s port %s. This port is already connected from task %s port %s" % (to_port.task().name, to_port.name, from_port.task().name, from_port.name, to_port.input_connections[0].from_port.task().name, to_port.input_connections[0].from_port.name))
    #
    #print 'connecting',from_port.task.id, to_port.task.id
    connector = cls(from_port=from_port, to_port=to_port)
    to_port.input_connections.append( connector )
    from_port.output_connections.append(connector)


class Port(object):
    """A class that represents an input or output port on a task."""

    def __init__(self, name, task, optional=False, value=None, action=None, constant=False, default=None, doc=None):
        """Constructor."""
        self.name=name
        # tasks are stored as weak refs, to prevent issues with cyclic dependencies and the garbage collector.
        self.task=weakref.ref(task)
        if action is None:
            self.action = 'store'
        else:
            self.action = action
        self.optional=optional
        self.constant=constant
        self.input_connections = []
        self.output_connections = []
        self.set_value(value)
        self._ready = False
        self.default=default
        self.doc=doc

    def reset(self):
        self._ready = False
        self.value = None

    def connect(self, port):
        """Define a connection with the specified port."""
        define_connection(DirectConnector, from_port=port, to_port=self)

    def from_tasks(self):
        """Return the id of the preceding task."""
        return [c.from_port.task() for c in self.input_connections if c.from_port.task() != None] 

    def get_value(self):
        """Get the value of this port."""
        if self.value is None:
            return self.default
        return self.value

    def set_value(self, value):
        """Set the value of this port."""
        self.value = value

    def compute_value(self):
        """Compute the value from the input connections."""
        #print 'X',self.name, self.action, len(self.input_connections)
        if self.action == 'store':
            if len(self.input_connections) == 1:
                val = self.input_connections[0].get_value()
                if not val is None:
                    self.value = val

        elif self.action == 'store_any':
            for connection in self.input_connections:
                if not connection.ready():
                    continue
                val = connection.get_value()
                if not val is None:
                    self.value = val
                    break

        elif self.action in ['append', 'append_any']:
            tmp = []
            for connection in self.input_connections:
                val = connection.get_value()
                if not val is None:
                    tmp.append( val )
            if len(tmp) > 0:
                self.value = tmp

        elif self.action in ['map', 'map_any']:
            tmp = {}
            for connection in self.input_connections:
                val = connection.get_value()
                if not val is None:
                    tmp[connection.from_port.task().id] = val
            if len(tmp) > 0:
                self.value = tmp

        self.validate()

    def validate(self):
        if self.action in ['store', 'store_any']:
            if not self.optional and self.get_value() is None:
                raise ValueError("Task %s Port %s requires a nontrivial value.  Value specified is None." % (str(self.task().id), self.name))
        #
        elif self.action in ['append', 'append_any']:
            if not self.optional and self.get_value() is None:
                raise ValueError("Task %s Port %s requires a nontrivial value.  All input connections have value None." % (str(self.task().id), self.name))
        #
        elif self.action in ['map', 'map_any']:
            if not self.optional and self.get_value() is None:
                raise ValueError("Task %s Port %s requires a nontrivial value.  All input connections have value None." % (str(self.task().id), self.name))

    def _repn_(self):
        tmp = {}
        tmp['A_TYPE'] = 'Port'
        tmp['Name'] = self.name
        tmp['Task'] = str(self.task().id)
        tmp['Optional'] = str(self.optional)
        tmp['Constant'] = str(self.constant)
        tmp['Value'] = str(self.value)
        tmp['Ready'] = str(self.ready())
        tmp['Action'] = self.action
        tmp['Connections'] = {}
        tmp['Connections']['Inputs'] = []
        for c in self.input_connections:
            tmp['Connections']['Inputs'].append(repr(c))
        tmp['Connections']['Outputs'] = []
        for c in self.output_connections:
            tmp['Connections']['Outputs'].append(repr(c))
        return tmp

    def __repr__(self):
        return str(self)    #pragma:nocover

    def __str__(self, indentation=""):
        return pprint.pformat(self._repn_(), 2) #pragma:nocover

    def ready(self):
        if not self.get_value() is None:
            return True
        if len(self.input_connections) == 0:
            return self._ready
        if self.action == 'store':
            return self.input_connections[0].ready()
        elif self.action in ['append_any', 'map_any', 'store_any']:
            for connection in self.input_connections:
                if connection.ready():
                    return True
            return False
        elif self.action in ['append', 'map']:
            for connection in self.input_connections:
                if not connection.ready():
                    return False
            return True
        #
        # We should never get here.
        #
        raise IOError("WARNING: unknown action: "+self.action)  #pragma:nocover

    def set_ready(self):
        self._ready=True


class Ports(dict):
    """A class that specifies a set of ports."""

    def __init__(self, task):
        """Constructor."""
        self._name_='Ports'
        # tasks are stored as weak refs, to prevent issues with cyclic dependencies and the garbage collector.
        self._task = weakref.ref(task)
        self._inputs=False
        self._outputs=False

    def set_name(self, name):
        """Set the name of this class instance."""
        self._name_ = name

    def declare(self, name, optional=False, action=None, constant=False, default=None, doc=None):
        """Declare a port."""
        port = Port(name, self._task(), optional=optional, action=action, constant=constant, default=default, doc=doc)
        setattr(self, name, port)
        return port

    def __setitem__(self, name, val):
        """Overload this operator to set an attribute with the specified name."""
        self.__setattr__(name,val)

    def __getitem__(self, name):
        """Overload this operator to get the attribute with the specified name."""
        return self.__getattr__(name)

    def __setattr__(self, name, val):
        """Overload this operator to setup a connection."""
        #
        # Directly set attributes whose names begin with '_'
        #
        if name[0] == '_':
            self.__dict__[name] = val
            return
        #
        # Declare a port
        #
        if not name in self.__dict__:
            if not isinstance(val, Port):
                raise TypeError("Error declaring port '%s' without a Port object" % name)
            dict.__setitem__(self, name, val)
            self.__dict__[name] = val
        #
        # Create a connection to another port
        #
        else:
            if not isinstance(val, Port):
                self.__dict__[name].set_value( val )
            else:
                self.__dict__[name].connect( val )

    def __getattr__(self, name):
        """Overload this operator to setup a connection."""
        try:
            return self.__dict__.__getitem__(name)
        except:
            raise AttributeError("Unknown attribute '%s'" % name)

    def _repn_(self):
        tmp = {}
        tmp['A_TYPE'] = 'Port'
        for k, v in self.__dict__.items():
            if not k.startswith("_"):
                tmp[k] = v._repn_()
        tmp['Name'] = self._name_
        if self._inputs:
            tmp['Mode'] = 'inputs'
        if self._outputs:
            tmp['Mode'] = 'outputs'
        # JPW: a port can't really exist independently of a task - we should check 
        #      this in the constructor.
        if self._task is not None:
            tmp['Owner'] = self._task()._name()
        return tmp
        

    def __repr__(self):                 #pragma:nocover
        """Return a string representation of these connections."""
        attrs = sorted("%s = %r" % (k, v) for k, v in self.__dict__.items() if not k.startswith("_"))
        return "%s(%s)" % (self.__class__.__name__, ", ".join(attrs))

    def __str__(self, nesting = 1, indent='',print_name=True):
        return pprint.pformat(self._repn_(), 2, width=150)


class InputPorts(Ports):
    """A class that is used to manage set of input ports."""

    def __init__(self, task):
        """Constructor."""
        Ports.__init__(self, task)
        self._inputs=True


class OutputPorts(Ports):
    """A class that is used to manage set of output ports."""

    def __init__(self, task):
        """Constructor."""
        Ports.__init__(self, task)
        self._outputs=True


