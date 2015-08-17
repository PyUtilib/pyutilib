#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

__all__ = ['TaskWorker','MultiTaskWorker','TaskWorkerServer']

import sys
import os
import socket
import time
import itertools
import random

from pyutilib.pyro import get_nameserver, using_pyro3, using_pyro4
from pyutilib.pyro import Pyro as _pyro
from pyutilib.pyro.util import get_dispatchers

from six import advance_iterator, iteritems, itervalues
from six.moves import xrange

_connection_problem = None
if using_pyro3:
    _connection_problem = _pyro.errors.ConnectionDeniedError
else:
    _connection_problem = _pyro.errors.TimeoutError

class TaskWorkerBase(object):

    def __init__(self,
                 group=":PyUtilibServer",
                 host=None,
                 num_dispatcher_tries=30,
                 caller_name="Task Worker",
                 verbose=False):

        self._verbose = verbose

        if _pyro is None:
            raise ImportError("Pyro or Pyro4 is not available")

        # Deprecated in Pyro3
        # Removed in Pyro4
        if using_pyro3:
            _pyro.core.initClient()

        self.ns = get_nameserver(host, caller_name=caller_name)
        if self.ns is None:
            raise RuntimeError("TaskWorkerBase failed to locate "
                               "Pyro name server on the network!")
        print('Worker attempting to find Pyro dispatcher object...')
        cumulative_sleep_time = 0.0
        self.dispatcher = None
        for i in xrange(0, num_dispatcher_tries):
            for name, uri in get_dispatchers(group=group, ns=self.ns):
                try:
                    if using_pyro3:
                        self.dispatcher = _pyro.core.getProxyForURI(uri)
                        # This forces Pyro3 to actually attempt to use
                        # the dispatcher proxy, which results in a
                        # connection denied error if the dispatcher
                        # proxy has reached its maximum allowed
                        # connections. DO NOT DELETE
                        self.dispatcher.queues_with_results()
                    else:
                        self.dispatcher = _pyro.Proxy(uri)
                        self.dispatcher._pyroTimeout = 1
                        self.dispatcher._pyroBind()
                except _connection_problem:
                    self.dispatcher = None
                else:
                    break
            if self.dispatcher is not None:
                if using_pyro4:
                    self.dispatcher._pyroTimeout = None
                break
            sleep_interval = random.uniform(5.0, 15.0)
            print("Worker failed to find dispatcher object from "
                  "name server after %d attempts and %5.2f seconds "
                  "- trying again in %5.2f seconds."
                  % (i+1, cumulative_sleep_time, sleep_interval))
            time.sleep(sleep_interval)
            cumulative_sleep_time += sleep_interval

        if self.dispatcher is None:
            raise RuntimeError(
                "Worker could not find dispatcher object - giving up")

        # There is no need to retain the proxy connection to the
        # nameserver, so free up resources on the nameserver thread
        URI = None
        if using_pyro4:
            self.ns._pyroRelease()
            URI = self.dispatcher._pyroUri
        else:
            self.ns._release()
            URI = self.dispatcher.URI

        self.WORKERNAME = "Worker_%d@%s" % (os.getpid(),
                                            socket.gethostname())
        print("Connection to dispatch server %s established "
              "after %d attempts and %5.2f seconds - "
              "this is worker: %s"
              % (URI, i+1, cumulative_sleep_time, self.WORKERNAME))

        # Do not release the connection to the dispatcher
        # We use this functionality to distribute workers across
        # multiple dispatchers based off of denied connections

    def _get_request_type(self):
        raise NotImplementedError("This is an abstract method")

    def run(self):

        print("Listening for work from dispatcher...")

        while 1:
            current_type, blocking, timeout = \
                self._get_request_type()
            try:
                task = self.dispatcher.get_task(type=current_type,
                                                block=blocking,
                                                timeout=timeout)
            except _connection_problem as e:
                x = sys.exc_info()[1]
                # this can happen if the dispatcher is overloaded
                print("***WARNING: Connection to dispatcher server "
                      "denied\n - exception type: "+str(type(e))+
                      "\n - message: "+str(x))
                print("A potential remedy may be to increase "
                      "PYUTILIB_PYRO_MAXCONNECTIONS in your shell "
                      "environment.")
                # sleep for a bit longer than normal, for obvious reasons
                sleep_interval = random.uniform(0.05, 0.15)
                time.sleep(sleep_interval) 
            else:
                if task is not None:

                    task['result'] = self.process(task['data'])
                    if task['generateResponse']:
                        task['processedBy'] = self.WORKERNAME
                        self.dispatcher.add_result(task, type=current_type)

class TaskWorker(TaskWorkerBase):

    def __init__(self, type=None, block=True, timeout=5, *args, **kwds):

        self.type = type
        self.block = block
        self.timeout = timeout

        TaskWorkerBase.__init__(self, *args, **kwds)

    # Called by the run() method to get the work type
    # including blocking and timeout options
    def _get_request_type(self):
        return self.type, self.block, self.timeout

class MultiTaskWorker(TaskWorkerBase):

    def __init__(self,
                 type_default=None,
                 block_default=True,
                 timeout_default=5,
                 *args,
                 **kwds):

        TaskWorkerBase.__init__(self, *args, **kwds)

        #
        # **NOTE: For this class 'type' is
        # a tuple (type, blocking, timeout, local)
        #
        self._num_types = 0
        self._type_cycle = None
        self.push_request_type(type_default,
                               block_default,
                               timeout_default)

    # Called by the run() method to get the next work type to request,
    # moves index to the next location in the cycle
    def _get_request_type(self):
        new = None
        try:
            new = advance_iterator(self._type_cycle)
        except StopIteration:
            raise RuntimeError("MultiTaskWorker has no work request types!")
        return new

    def current_type_order(self):
        """
        return the full work type list, starting from the current
        location in the cycle.
        """
        if self._num_types == 0:
            return []
        type_list = []
        for cnt in xrange(self._num_types):
            type_list.append(advance_iterator(self._type_cycle))
        return type_list

    def cycle_type_order(self):
        advance_iterator(self._type_cycle)

    def num_request_types(self):
        return self._num_types

    def clear_request_types(self):
        self._type_cycle = itertools.cycle([])
        self._num_types = 0

    def push_request_type(self, type_name, block, timeout):
        """
        add a request type to the end relative to the current cycle
        location
        """
        self._type_cycle = itertools.cycle(self.current_type_order() + \
                                           [(type_name, block, timeout)])
        self._num_types += 1

    def pop_request_type(self):
        """
        delete the last type request relative to the current cycle
        location
        """
        new_type_list = self.current_type_order()
        el = new_type_list.pop()
        self._type_cycle = itertools.cycle(new_type_list)
        self._num_types -= 1
        return el

    def run(self):

        print("Listening for work from dispatcher...")

        while 1:
            tasks = []
            try:
                tasks = self.dispatcher.get_tasks(self.current_type_order())
                #if using_pyro4:
                #    self.dispatcher._pyroRelease()
                #else:
                #    self.dispatcher._release()
            except _connection_problem as e:
                x = sys.exc_info()[1]
                # this can happen if the dispatcher is overloaded
                print("***WARNING: Connection to dispatcher server "
                      "denied\n - exception type: "+str(type(e))+
                      "\n - message: "+str(x))
                print("A potential remedy may be to increase "
                      "PYUTILIB_PYRO_MAXCONNECTIONS in your shell "
                      "environment.")
                # sleep for a bit longer than normal, for obvious reasons
                sleep_interval = random.uniform(0.05, 0.15)
                time.sleep(sleep_interval)
            else:

                if len(tasks) > 0:

                    if self._verbose:
                        print("Processing %s tasks from %s queue(s)"
                              % (sum(len(_tl) for _tl in itervalues(tasks)),
                                 len(tasks)))

                    results = dict.fromkeys(tasks)
                    # process tasks by type in order of increasing id
                    for type_name, type_tasks in iteritems(tasks):
                        type_results = results[type_name] = []
                        for task in sorted(type_tasks, key=lambda x: x['id']):
                            task['result'] = self.process(task['data'])
                            if task['generateResponse']:
                                task['processedBy'] = self.WORKERNAME
                                type_results.append(task)
                        if len(type_results) == 0:
                            del results[type_name]

                    if len(results):
                        self.dispatcher.add_results(results)

def TaskWorkerServer(cls, **kwds):
    host=None
    if 'argv' in kwds:
        argv = kwds['argv']
        if len(argv) == 2:
            host=argv[1]
        kwds['host'] = host
        del kwds['argv']
    worker = cls(**kwds)
    if worker.ns is None:
        return
    try:
        worker.run()
    except _pyro.errors.ConnectionClosedError:
        print("Lost connection to dispatch server - shutting down...")
