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

#
# Setup the timer
#
if sys.version_info >= (3,3):
    # perf_counter is guaranteed to be monotonic and the most accurate timer
    _time_source = time.perf_counter
else:
    # On old Pythons, clock() is more accurate than time() on Windows
    # (.35us vs 15ms), but time() is more accurate than clock() on Linux
    # (1ns vs 1us).  It is unfortunate that time() is not monotonic, but
    # since the TicTocTimer is used for (potentially very accurate)
    # timers, we will sacrifice monotonicity on Linux for resolution.
    if sys.platform.startswith('win'):
        _time_source = time.clock
    else:
        _time_source = time.time

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
        self._lastTime = self._loadTime = _time_source()
        self._ostream = ostream
        self._logger = logger
        self._start_count = 0
        self._cumul = 0

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
        self._lastTime = _time_source()
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

        if msg is None:
            msg = 'File "%s", line %s in %s' % \
                  traceback.extract_stack(limit=2)[0][:3]

        now = _time_source()
        if self._start_count or self._lastTime is None:
            ans = self._cumul
            if self._lastTime:
                ans += _time_source() - self._lastTime
            if msg:
                msg = "[%8.2f|%4d] %s\n" % (ans, self._start_count, msg)
        elif delta:
            ans = now - self._lastTime
            self._lastTime = now
            if msg:
                msg = "[+%7.2f] %s\n" % (ans, msg)
        else:
            ans = now - self._loadTime
            if msg:
                msg = "[%8.2f] %s\n" % (ans, msg)

        if msg:
            if ostream is None:
                ostream = self._ostream
                if ostream is None and logger is None:
                    ostream = sys.stdout
            if ostream is not None:
                ostream.write(msg)

            if logger is None:
                logger = self._logger
            if logger is not None:
                logger.info(msg)

        return ans

    def stop(self):
        try:
            delta = _time_source() - self._lastTime
        except TypeError:
            if self._lastTime is None:
                raise RuntimeError(
                    "Stopping a TicTocTimer that was already stopped")
            raise
        self._cumul += delta
        self._lastTime = None
        return delta

    def start(self):
        if self._lastTime:
            self.stop()
        self._start_count += 1
        self._lastTime = _time_source()

_globalTimer = TicTocTimer()
tic = _globalTimer.tic
toc = _globalTimer.toc


class _HierarchicalHelper(object):
    def __init__(self):
        self.total_time = 0
        self.t0 = None
        self.n_calls = 0
        self.timers = dict()

    def start_increment(self):
        self.t0 = time.time()

    def stop_increment(self):
        self.total_time += time.time() - self.t0
        self.n_calls += 1

    def print(self, indent):
        s = ''
        if len(self.timers) > 0:
            max_name_len = 12
            for name in self.timers.keys():
                if len(name) > max_name_len:
                    max_name_len = len(name)
            name_formatter = '{name:<' + str(max_name_len) + '}'
            s += indent
            s += (name_formatter +
                  '{total_time:>15}'
                  '{num_calls:>15}'
                  '{time_per_call:>15}'
                  '{relative_percent:>15}\n').format(name='Identifier',
                                                     total_time='Time (s)',
                                                     num_calls='# Calls',
                                                     time_per_call='Per Call(s)',
                                                     relative_percent='% Time')
            other_time = self.total_time
            for name, timer in self.timers.items():
                s += indent
                s += name_formatter.format(name=name)
                s += '{0:>15.2e}'.format(timer.total_time)
                s += '{0:>15d}'.format(timer.n_calls)
                s += '{0:>15.2e}'.format(timer.total_time/timer.n_calls)
                s += '{0:>15.1f}%\n'.format(timer.total_time/self.total_time*100)
                s += timer.print(indent=indent + '    ')
                other_time -= timer.total_time
            s += indent
            s += name_formatter.format(name='other')
            s += '{0:>15.2e}'.format(other_time)
            s += '{0:>15}'.format('N/A')
            s += '{0:>15}'.format('N/A')
            s += '{0:>15.1f}%\n'.format(other_time / self.total_time * 100)
        return s


class HierarchicalTimer(object):
    def __init__(self):
        self.stack = list()
        self.timers = dict()

    def _get_timer(self, identifier, should_exist=False):
        parent = self._get_timer_from_stack(self.stack)
        if identifier in parent.timers:
            return parent.timers[identifier]
        else:
            if should_exist:
                raise RuntimeError('Could not find timer {0}'.format('.'.join(self.stack + [identifier])))
            parent.timers[identifier] = _HierarchicalHelper()
            return parent.timers[identifier]

    def start_increment(self, identifier):
        timer = self._get_timer(identifier)
        timer.start_increment()
        self.stack.append(identifier)

    def stop_increment(self, identifier):
        assert identifier == self.stack.pop()
        timer = self._get_timer(identifier, should_exist=True)
        timer.stop_increment()

    def __str__(self):
        max_name_len = 12
        for name in self.timers.keys():
            if len(name) > max_name_len:
                max_name_len = len(name)
        name_formatter = '{name:<' + str(max_name_len) + '}'
        s = (name_formatter +
             '{total_time:>15}'
             '{num_calls:>15}'
             '{time_per_call:>15}\n').format(name='Identifier',
                                             total_time='Time (s)',
                                             num_calls='# Calls',
                                             time_per_call='Per Call (s)')
        for name, timer in self.timers.items():
            s += name_formatter.format(name=name)
            s += '{0:>15.2e}'.format(timer.total_time)
            s += '{0:>15d}'.format(timer.n_calls)
            s += '{0:>15.2e}\n'.format(timer.total_time/timer.n_calls)
            s += timer.print(indent='    ')
        return s

    def reset(self):
        self.stack = list()
        self.timers = dict()

    def _get_timer_from_stack(self, stack):
        tmp = self
        for i in stack:
            tmp = tmp.timers[i]
        return tmp

    def get_total_time(self, identifier):
        stack = identifier.split('.')
        timer = self._get_timer_from_stack(stack)
        return timer.total_time

    def get_num_calls(self, identifier):
        stack = identifier.split('.')
        timer = self._get_timer_from_stack(stack)
        return timer.n_calls

    def get_relative_percent_time(self, identifier):
        stack = identifier.split('.')
        timer = self._get_timer_from_stack(stack)
        parent = self._get_timer_from_stack(stack[:-1])
        return timer.total_time / parent.total_time * 100

    def get_total_percent_time(self, identifier):
        stack = identifier.split('.')
        timer = self._get_timer_from_stack(stack)
        total_time = 0
        for _timer in self.timers.values():
            total_time += _timer.total_time
        return timer.total_time / total_time * 100
