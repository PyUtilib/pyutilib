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
        self.tic_toc = TicTocTimer()
        self.timers = dict()
        self.total_time = 0
        self.n_calls = 0

    def start(self):
        self.n_calls += 1
        self.tic_toc.start()

    def stop(self):
        self.total_time += self.tic_toc.stop()

    def pprint(self, indent, stage_identifier_lengths):
        s = ''
        if len(self.timers) > 0:
            underline = indent + '-' * (sum(stage_identifier_lengths) + 46) + '\n'
            s += underline
            name_formatter = '{name:<' + str(sum(stage_identifier_lengths)) + '}'
            other_time = self.total_time
            sub_stage_identifier_lengths = stage_identifier_lengths[1:]
            for name, timer in self.timers.items():
                s += indent
                s += name_formatter.format(name=name)
                s += '{ncalls:>12d}'.format(ncalls=timer.n_calls)
                s += '{cumtime:>12.3f}'.format(cumtime=timer.total_time)
                s += '{percall:>12.3f}'.format(percall=timer.total_time/timer.n_calls)
                if self.total_time > 0:
                    s += '{percent:>10.1f}\n'.format(percent=timer.total_time / self.total_time * 100)
                else:
                    s += '{percent:>10}\n'.format(percent='nan')
                s += timer.pprint(indent=indent + ' '*stage_identifier_lengths[0],
                                  stage_identifier_lengths=sub_stage_identifier_lengths)
                other_time -= timer.total_time
            s += indent
            s += name_formatter.format(name='other')
            s += '{ncalls:>12}'.format(ncalls='N/A')
            s += '{cumtime:>12.3f}'.format(cumtime=other_time)
            s += '{percall:>12}'.format(percall='N/A')
            if self.total_time > 0:
                s += '{percent:>10.1f}\n'.format(percent=other_time / self.total_time * 100)
            else:
                s += '{percent:>10}\n'.format(percent='nan')
            s += underline.replace('-', '=')
        return s


class HierarchicalTimer(object):
    """
    A class for hierarchical timing.

    Examples
    --------
    >>> from pyutilib.misc.timing import HierarchicalTimer
    >>> timer = HierarchicalTimer()
    >>> timer.start('all')
    >>> for i in range(10):
    >>>     timer.start('a')
    >>>     for i in range(5):
    >>>         timer.start('aa')
    >>>         timer.stop('aa')
    >>>     timer.start('ab')
    >>>     timer.stop('ab')
    >>>     timer.stop('a')
    >>> for i in range(10):
    >>>     timer.start('b')
    >>>     timer.stop('b')
    >>> timer.stop('all')
    >>> print(timer)
    Identifier           ncalls  cumtime(s)  percall(s)         %
    -------------------------------------------------------------
    all                       1       0.000       0.000     100.0
         --------------------------------------------------------
         a                   10       0.000       0.000      79.2
              ---------------------------------------------------
              aa             50       0.000       0.000      35.6
              ab             10       0.000       0.000       6.9
              other         N/A       0.000         N/A      57.5
              ===================================================
         b                   10       0.000       0.000       5.3
         other              N/A       0.000         N/A      15.6
         ========================================================
    =============================================================

    The columns are:
    ncalls     : The number of times the timer was started and stopped
    cumtime (s): The cumulative time the timer was active (started but not stopped)
    percall (s): cumtime / ncalls
    %          : This is cumtime of the timer divided by cumtime of the parent timer times 100


    >>> print('a total time: ', timer.get_total_time('all.a'))
    a total time:  0.11518359184265137
    >>> 
    >>> print('ab num calls: ', timer.get_num_calls('all.a.ab'))
    ab num calls:  10
    >>> 
    >>> print('aa % time: ', timer.get_relative_percent_time('all.a.aa'))
    aa % time:  57.28656738043737
    >>>
    >>> print('aa % of total time: ', timer.get_total_percent_time('all.a.aa'))
    aa % of total time:  50.96888018003749

    Internal Workings
    -----------------
    The HierarchicalTimer use a stack to track which timers are active
    at any point in time. Additionally, each timer has a dictionary of
    timers for its children timers. Consider

    >>> timer = HierarchicalTimer()
    >>> timer.start('all')
    >>> timer.start('a')
    >>> timer.start('aa')

    After the above code is run, self.stack will be ['all', 'a', 'aa']
    and self.timers will have one key, 'all' and one value which will
    be a _HierarchicalHelper. The _HierarchicalHelper has its own timers dictionary: 
    
    {'a': _HierarchicalHelper}

    and so on. This way, we can easily access any timer with something
    that looks like the stack. The logic is recursive (although the
    code is not).

    """
    def __init__(self):
        self.stack = list()
        self.timers = dict()

    def _get_timer(self, identifier, should_exist=False):
        """

        This method gets the timer associated with the current state
        of self.stack and the specified identifier.

        Parameters
        ----------
        identifier: str
            The name of the timer
        should_exist: bool
            The should_exist is True, and the timer does not already
            exist, an error will be raised. If should_exist is False, and
            the timer does not already exist, a new timer will be made.
        
        Returns
        -------
        timer: _HierarchicalHelper

        """
        parent = self._get_timer_from_stack(self.stack)
        if identifier in parent.timers:
            return parent.timers[identifier]
        else:
            if should_exist:
                raise RuntimeError('Could not find timer {0}'.format('.'.join(self.stack + [identifier])))
            parent.timers[identifier] = _HierarchicalHelper()
            return parent.timers[identifier]

    def start(self, identifier):
        """
        Start incrementing the timer identified with identifier

        Parameters
        ----------
        identifier: str
            The name of the timer
        """
        timer = self._get_timer(identifier)
        timer.start()
        self.stack.append(identifier)

    def stop(self, identifier):
        """
        Stop incrementing the timer identified with identifier

        Parameters
        ----------
        identifier: str
            The name of the timer
        """
        if identifier != self.stack[-1]:
            raise ValueError(str(identifier) + ' is not the currently active timer. The only timer that can currently be stopped is ' + '.'.join(self.stack))
        self.stack.pop()
        timer = self._get_timer(identifier, should_exist=True)
        timer.stop()

    def _get_identifier_len(self):
        stage_timers = list(self.timers.items())
        stage_lengths = list()

        while len(stage_timers) > 0:
            new_stage_timers = list()
            max_len = 0
            for identifier, timer in stage_timers:
                new_stage_timers.extend(timer.timers.items())
                if len(identifier) > max_len:
                    max_len = len(identifier)
            stage_lengths.append(max(max_len, len('other')))
            stage_timers = new_stage_timers

        return stage_lengths

    def __str__(self):
        stage_identifier_lengths = self._get_identifier_len()
        name_formatter = '{name:<' + str(sum(stage_identifier_lengths)) + '}'
        s = (name_formatter +
             '{ncalls:>12}'
             '{cumtime:>12}'
             '{percall:>12}'
             '{percent:>10}\n').format(name='Identifier',
                                      ncalls='ncalls',
                                      cumtime='cumtime(s)',
                                      percall='percall(s)',
                                      percent='%')
        underline = '-' * (sum(stage_identifier_lengths) + 46) + '\n'
        s += underline
        sub_stage_identifier_lengths = stage_identifier_lengths[1:]
        for name, timer in self.timers.items():
            s += name_formatter.format(name=name)
            s += '{ncalls:>12d}'.format(ncalls=timer.n_calls)
            s += '{cumtime:>12.3f}'.format(cumtime=timer.total_time)
            s += '{percall:>12.3f}'.format(percall=timer.total_time/timer.n_calls)
            s += '{percent:>10.1f}\n'.format(percent=self.get_total_percent_time(name))
            s += timer.pprint(indent=' '*stage_identifier_lengths[0],
                              stage_identifier_lengths=sub_stage_identifier_lengths)
        s += underline.replace('-', '=')
        return s

    def reset(self):
        """
        Completely reset the timer.
        """
        self.stack = list()
        self.timers = dict()

    def _get_timer_from_stack(self, stack):
        """
        This method gets the timer associated with stack.

        Parameters
        ----------
        stack: list of str
            A list of identifiers. 
        
        Returns
        -------
        timer: _HierarchicalHelper
        """
        tmp = self
        for i in stack:
            tmp = tmp.timers[i]
        return tmp

    def get_total_time(self, identifier):
        """
        Parameters
        ----------
        identifier: str
            The full name of the timer including parent timers separated with dots.

        Returns
        -------
        total_time: float
            The total time spent with the specified timer active.
        """
        stack = identifier.split('.')
        timer = self._get_timer_from_stack(stack)
        return timer.total_time

    def get_num_calls(self, identifier):
        """
        Parameters
        ----------
        identifier: str
            The full name of the timer including parent timers separated with dots.

        Returns
        -------
        num_calss: int
            The number of times start was called for the specified timer.
        """
        stack = identifier.split('.')
        timer = self._get_timer_from_stack(stack)
        return timer.n_calls

    def get_relative_percent_time(self, identifier):
        """
        Parameters
        ----------
        identifier: str
            The full name of the timer including parent timers separated with dots.

        Returns
        -------
        percent_time: float
            The percent of time spent in the specified timer 
            relative to the timer's immediate parent.
        """
        stack = identifier.split('.')
        timer = self._get_timer_from_stack(stack)
        parent = self._get_timer_from_stack(stack[:-1])
        if parent is self:
            return self.get_total_percent_time(identifier)
        else:
            if parent.total_time > 0:
                return timer.total_time / parent.total_time * 100
            else:
                return float('nan')

    def get_total_percent_time(self, identifier):
        """
        Parameters
        ----------
        identifier: str
            The full name of the timer including parent timers separated with dots.

        Returns
        -------
        percent_time: float
            The percent of time spent in the specified timer 
            relative to the total time in all timers.
        """
        stack = identifier.split('.')
        timer = self._get_timer_from_stack(stack)
        total_time = 0
        for _timer in self.timers.values():
            total_time += _timer.total_time
        if total_time > 0:
            return timer.total_time / total_time * 100
        else:
            return float('nan')
