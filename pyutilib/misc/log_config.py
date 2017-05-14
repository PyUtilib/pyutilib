#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

import inspect
import logging
import os
import sys

from pyutilib.misc.indent_io import StreamIndenter

class LogHandler(logging.Handler):

    def __init__( self, base='', stream=sys.stdout, 
                  level=logging.NOTSET, verbosity=None ):
        if verbosity is not None:
            self.verbosity = verbosity
        else:
            self.verbosity = lambda: True
        logging.Handler.__init__(self, level=level)

        self.stream = stream
        self.basepath = base

    def emit(self, record):
        level = record.levelname
        msg = record.getMessage()

        if self.verbosity():
            filename = record.pathname  # file path
            lineno = record.lineno
            try:
                function = record.funcName
            except AttributeError:
                function = '(unknown)'
            if self.basepath and filename.startswith(self.basepath):
                filename = '[base]' + filename[len(self.basepath):]

            self.stream.write(
                '%s: "%s", %d, %s\n' %
                ( level, filename, lineno, function.strip(), ))
            StreamIndenter(self.stream, "\t").write(msg.strip() + "\n")
        else:
            lines = msg.strip().splitlines(False)
            self.stream.write('%s: %s\n' % (
                level, '\n\t'.join(lines) ))

# Set up default logging for PyUtilib
pyutilib_base = os.path.normpath(os.path.join(
    os.path.dirname( os.path.abspath(
        inspect.getframeinfo(inspect.currentframe()).filename)),
    '..', '..', '..'))

logger = logging.getLogger('pyutilib')
logger.setLevel(logging.WARNING)
logger.addHandler(
    LogHandler(
        pyutilib_base, verbosity=lambda: logger.isEnabledFor(logging.DEBUG)))
