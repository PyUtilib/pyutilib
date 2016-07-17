#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

import logging
from pyutilib.misc.indent_io import StreamIndenter


class LogHandler(logging.Handler):

    def __init__(self, base, *args, **kwargs):
        if 'verbosity' in kwargs:
            self.verbosity = kwargs.pop('verbosity')
        else:
            self.verbosity = lambda: True
        logging.Handler.__init__(self, *args, **kwargs)

        self.basepath = base

    def emit(self, record):
        import sys  # why?  Isn't this imported above?
        # Doesn't work w/o it though ... ?

        level = record.levelname
        filename = record.pathname  # file path
        lineno = record.lineno
        msg = record.getMessage()
        try:
            function = record.funcName
        except AttributeError:
            function = '(unknown)'

        filename = filename.replace(self.basepath, '[base]')

        if self.verbosity():
            sys.stdout.write('%(level)s: "%(fpath)s", %(lineno)d, '
                             '%(caller)s\n' % {
                                 'level': level,
                                 'fpath': filename,
                                 'lineno': lineno,
                                 'caller': function.strip(),
                             })
            StreamIndenter(sys.stdout, "\t").write(msg.strip() + "\n")
        else:
            lines = msg.splitlines(True)
            sys.stdout.write('%(level)s: %(msg)s\n' % {
                'level': level,
                'msg': lines and lines.pop(0).strip() or '\n',
            })
            if lines:
                StreamIndenter(sys.stdout, "\t").writelines(lines)
                if len(lines[-1]) and lines[-1][-1] != '\n':
                    sys.stdout.write('\n')

# Set up default logging for PyUtilib
from os.path import abspath, dirname, join, normpath
pyutilib_base = normpath(join(dirname(abspath(__file__)), '..', '..', '..'))

logger = logging.getLogger('pyutilib')
logger.setLevel(logging.WARNING)
logger.addHandler(
    LogHandler(
        pyutilib_base, verbosity=lambda: logger.isEnabledFor(logging.DEBUG)))
