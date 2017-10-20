#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________
#

import sys
import time
import traceback

__all__ = ('TicTocTimer', 'tic', 'toc')

_loadTime = time.time()

class TicTocTimer(object):
    """A class to calculate and report elapsed time.

    Examples:
       >>> from pyutilib.misc.timing import TicTocTimer
       >>> timer = TicTocTimer()
       >>> timer.tic('starting timer') # starts the elapsed time timer (from 0)
       >>> # ... do task 1
       >>> timer.toc('task 1') # prints the elapsed time for task 1

    If no ostream or logger is provided, then output is printed to sys.stdout

    Args:
        ostream (FILE): an optional output stream to print the timing
            information
        logger (Logger): an optional output stream using the python
           logging package. Note: timing logged using logger.info
    """
    def __init__(self, ostream=None, logger=None):
        self._lastTime = time.time()
        self._ostream = ostream
        self._logger = logger

    def tic(self, msg=None, ostream=None, logger=None):
        """Reset the tic/toc delta timer.

        This resets the reference time from which the next delta time is
        calculated to the current time.

        Args:
            msg (str): The message to print out.  If :const:`None`
                (default), then prints out "Resetting the tic/toc delta
                timer"; if it evaluates to :const:`False` (:const:`0`,
                :const:`False`, :const:`""`) then no message is printed.
            ostream (FILE): an optional output stream (overrides the ostream
                provided when the class was constructed).
            logger (Logger): an optional output stream using the python
                logging package (overrides the ostream provided when the
                class was constructed). Note: timing logged using logger.info
        """
        self._lastTime = time.time()
        if msg is None:
            msg = "Resetting the tic/toc delta timer"
        if msg:
            self.toc(msg=msg, delta=False, ostream=ostream, logger=logger)


    def toc(self, msg=None, delta=True, ostream=None, logger=None):
        """Print out the elapsed time.

        This resets the reference time from which the next delta time is
        calculated to the current time.

        Args:
            msg (str): The message to print out.  If :const:`None`
                (default), then print out the file name, line number,
                and function that called this method; if it evaluates to
                :const:`False` (:const:`0`, :const:`False`, :const:`""`)
                then no message is printed.
            delta (bool): print out the elapsed wall clock time since
                the last call to :meth:`tic` or :meth:`toc`
                (:const:`True` (default)) or since the module was first
                loaded (:const:`False`).
            ostream (FILE): an optional output stream (overrides the ostream
                provided when the class was constructed).
            logger (Logger): an optional output stream using the python
                logging package (overrides the ostream provided when the
                class was constructed). Note: timing logged using logger.info
        """
        now = time.time()
        if delta:
            ans = now - self._lastTime
            self._lastTime = now
        else:
            ans = now - _loadTime

        if msg is None:
            msg = 'File "%s", line %s in %s' % \
                  traceback.extract_stack(limit=2)[0][:3]
        if msg:
            if ostream is None:
                ostream = self._ostream
                if ostream is None and logger is None:
                    ostream = sys.stdout
                
            if ostream is not None:
                if delta:
                    ostream.write("[+%7.2f] %s\n" % (ans, msg))
                else:
                    ostream.write("[%8.2f] %s\n" % (ans, msg))

            if logger is None:
                logger = self._logger

            if logger is not None:
                if delta:
                    logger.info("[+%7.2f] %s\n" % (ans, msg))
                else:
                    logger.info("[%8.2f] %s\n" % (ans, msg))

        return ans

_globalTimer = TicTocTimer()
tic = _globalTimer.tic
toc = _globalTimer.toc
