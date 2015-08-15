#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

__all__ = ['Dispatcher', 'DispatcherServer']

import os
import sys
from collections import defaultdict

from pyutilib.pyro import get_nameserver, using_pyro3, using_pyro4
from pyutilib.pyro import Pyro as _pyro

if sys.version_info >= (3,0):
    import queue as Queue
else:
    import Queue

from six import iteritems

if using_pyro3:
    base = _pyro.core.ObjBase
    oneway = lambda method: method
elif using_pyro4:
    base = object
    oneway = _pyro.oneway
else:
    base = object
    oneway = lambda method: method

class Dispatcher(base):

    def __init__(self, **kwds):
        if _pyro is None:
            raise ImportError("Pyro or Pyro4 is not available")
        if using_pyro3:
            _pyro.core.ObjBase.__init__(self)
        self.task_queue = defaultdict(Queue.Queue)
        self.result_queue = defaultdict(Queue.Queue)
        self.verbose = kwds.get("verbose", False)
        if self.verbose:
           print("Verbose output enabled...")

    @oneway
    def shutdown(self):
        print("Dispatcher received request to shut down - initiating...")
        if using_pyro3:
            self.getDaemon().shutdown()
        else:
            self._pyroDaemon.shutdown()

    @oneway
    def clear_queue(self, type=None):
        try:
            del self.task_queue[type]
        except KeyError:
            pass
        try:
            del self.result_queue[type]
        except KeyError:
            pass

    # process a set of tasks in one shot - the input
    # is a dictionary from queue type (including None)
    # to a list of tasks to be added to that queue.
    @oneway
    def add_tasks(self, tasks):
        if self.verbose:
           print("Received request to add bulk task set")
        for task_type in tasks:
            task_queue = self.task_queue[task_type]
            for task in tasks[task_type]:
                task_queue.put(task)

    @oneway
    def add_task(self, task, type=None):
        if self.verbose:
           print("Received request to add task=<Task id="
                 +str(task['id'])+">; queue type="+str(type))
        self.task_queue[type].put(task)

    def get_task(self, type=None, block=True, timeout=5):
        if self.verbose:
           print("Received request to get a task from "
                 "queue type="+str(type)+"; block="+str(block)+
                 "; timeout="+str(timeout)+" seconds")
        try:
            return self.task_queue[type].get(block=block,
                                             timeout=timeout)
        except Queue.Empty:
            return None

    def get_tasks(self, type_block_timeout_list):
        if self.verbose:
           print("Received request to get tasks in bulk. "
                 "Queue request types="+str(type_block_timeout_list))

        ret = {}
        for type, block, timeout in type_block_timeout_list:
            task_list = []
            try:
                task_list.append(self.task_queue[type].get(block=block,
                                                           timeout=timeout))
            except Queue.Empty:
                pass
            else:
                while self.task_queue[type].qsize():
                    try:
                        task_list.append(self.task_queue[type].get(block=block,
                                                                   timeout=timeout))
                    except Queue.Empty:
                        pass
            if len(task_list) > 0:
                ret.setdefault(type, []).extend(task_list)

        return ret

    # process a set of results in one shot - the input
    # is a dictionary from queue type (including None)
    # to a list of results to be added to that queue.
    @oneway
    def add_results(self, results):
        if self.verbose:
           print("Received request to add bulk result set")
        for result_type in results:
            result_queue = self.result_queue[result_type]
            for result in results[result_type]:
                result_queue.put(result)

    @oneway
    def add_result(self, result, type=None):
        if self.verbose:
           print("Received request to add result with "
                 "result="+str(result)+"; queue type="+str(type))
        self.result_queue[type].put(result)

    def get_result(self, type=None, block=True, timeout=5):
        if self.verbose:
           print("Received request to get a result from "
                 "queue type="+str(type)+"; block="+str(block)+
                 "; timeout="+str(timeout))
        try:
            return self.result_queue[type].get(block=block,
                                               timeout=timeout)
        except Queue.Empty:
            return None

    def num_tasks(self, type=None):
        if self.verbose:
           print("Received request for number of tasks in "
                 "queue with type="+str(type))
        return self.task_queue[type].qsize()

    def num_results(self, type=None):
        if self.verbose:
           print("Received request for number of results in "
                 "queue with type="+str(type))
        return self.result_queue[type].qsize()

    def queues_with_results(self):
        if self.verbose:
           print("Received request for the set of queues with results")

        results = []
        #
        # Iterate over a copy of the contents of the queue, since
        # the queue may change while iterating.
        #
        for queue_name, result_queue in list(self.result_queue.items()):
           if result_queue.qsize() > 0:
               results.append(queue_name)

        return results

    def get_results_all_queues(self):

        if self.verbose:
           print("Received request to obtain all available "
                 "results from all queues")

        results = []
        #
        # Iterate over a copy of the contents of the queue, since
        # the queue may change while iterating.
        #
        for queue_name, result_queue in list(self.result_queue.items()):

            while result_queue.qsize() > 0:
                try:
                    results.append(result_queue.get(block=False, timeout=0))
                except Queue.Empty:
                    pass

        return results


def DispatcherServer(group=":PyUtilibServer",
                     host=None,
                     verbose=False,
                     max_connections=None):

    if max_connections is None:
        max_pyro_connections_envname = "PYUTILIB_PYRO_MAXCONNECTIONS"
        if max_pyro_connections_envname in os.environ:
            new_val = int(os.environ[max_pyro_connections_envname])
            print("Setting maximum number of connections to dispatcher to "
                  +str(new_val)+", based on specification provided by "
                  +max_pyro_connections_envname+" environment variable")
            if using_pyro3:
                _pyro.config.PYRO_MAXCONNECTIONS = new_val
            else:
                _pyro.config.THREADPOOL_SIZE = new_val
    else:
        print("Setting maximum number of connections to dispatcher to "
              +str(new_val)+", based on dispatcher max_connections keyword")
        if using_pyro3:
            _pyro.config.PYRO_MAXCONNECTIONS = max_connections
        else:
            _pyro.config.THREADPOOL_SIZE = max_connections

    #
    # main program
    #
    ns = get_nameserver(host,caller_name="Dispatcher")
    if ns is None:
        return

    if using_pyro3:
        daemon = _pyro.core.Daemon()
        daemon.useNameServer(ns)
    else:
        daemon = _pyro.Daemon()

    if using_pyro3:
        try:
            ns.createGroup(group)
        except _pyro.errors.NamingError:
            pass
        try:
            ns.unregister(group+".dispatcher")
        except _pyro.errors.NamingError:
            pass
    else:
        try:
            ns.remove(group+".dispatcher")
        except _pyro.errors.NamingError:
            pass

    disp = Dispatcher(verbose=verbose)
    if using_pyro3:
        uri = daemon.connect(disp, group+".dispatcher")
    else:
        uri = daemon.register(disp, group+".dispatcher")
        ns.register(group+".dispatcher", uri)

    # There is no need to retain the proxy connection to the
    # nameserver, so free up resources on the nameserver thread
    if using_pyro4:
        ns._pyroRelease()
    else:
        ns._release()

    print("Dispatcher is ready.")
    daemon.requestLoop()
