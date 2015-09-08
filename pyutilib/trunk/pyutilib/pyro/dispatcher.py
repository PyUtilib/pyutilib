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
import uuid
from collections import defaultdict

from pyutilib.pyro import get_nameserver, using_pyro3, using_pyro4
from pyutilib.pyro import Pyro as _pyro
from pyutilib.pyro.util import set_maxconnections, get_dispatchers

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
        self._task_queue = defaultdict(Queue.Queue)
        self._result_queue = defaultdict(Queue.Queue)
        self._verbose = kwds.pop("verbose", False)
        self._registered_workers = set()
        self._acquired_workers = set()
        self._worker_limit = kwds.pop("worker_limit", None)
        if self._verbose:
           print("Verbose output enabled...")

    def acquire_available_workers(self):
        worker_names = self._registered_workers - self._acquired_workers
        self._acquired_workers.update(worker_names)
        return worker_names

    @oneway
    def release_acquired_workers(self, names):
        names = set(names)
        if not names.issubset(self._registered_workers):
            raise ValueError("List contains one or more worker names that "
                             "were not registered")
        self._acquired_workers.difference_update(names)

    def register_worker(self, name):
        if name in self._registered_workers:
            raise ValueError("Worker name '%s' has already been registered")
        if (self._worker_limit is None) or \
           (len(self._registered_workers) < self._worker_limit):
            self._registered_workers.add(name)
            if self._verbose:
                print("Registering worker %s with name: %s"
                      % (len(self._registered_workers), name))
            return True
        return False

    @oneway
    def unregister_worker(self, name):
        if name not in self._registered_workers:
            raise ValueError("Worker name '%s' has not been registered")
        if self._verbose:
            print("Unregistering worker %s with name: %s"
                  % (len(self._registered_workers.index(name)+1), name))
        self._registered_workers.remove(name)

    @oneway
    def shutdown(self):
        print("Dispatcher received request to shut down - initiating...")
        if using_pyro3:
            self.getDaemon().shutdown()
        else:
            self._pyroDaemon.shutdown()

    @oneway
    def clear_all_queues(self):
        self._task_queue = defaultdict(Queue.Queue)
        self._result_queue = defaultdict(Queue.Queue)

    @oneway
    def clear_queue(self, type=None):
        try:
            del self._task_queue[type]
        except KeyError:
            pass
        try:
            del self._result_queue[type]
        except KeyError:
            pass

    @oneway
    def clear_queues(self, types):
        for type in types:
            self.clear_queue(type=type)

    @oneway
    def add_task(self, task, type=None):
        if self._verbose:
           print("Received request to add task=<Task id="
                 +str(task['id'])+">; queue type="+str(type))
        self._task_queue[type].put(task)

    # process a set of tasks in one shot - the input
    # is a dictionary from queue type (including None)
    # to a list of tasks to be added to that queue.
    @oneway
    def add_tasks(self, tasks):
        if self._verbose:
           print("Received request to add bulk task set")
        for task_type in tasks:
            task_queue = self._task_queue[task_type]
            for task in tasks[task_type]:
                task_queue.put(task)

    def get_task(self, type=None, block=True, timeout=5):
        if self._verbose:
           print("Received request to get a task from "
                 "queue type="+str(type)+"; block="+str(block)+
                 "; timeout="+str(timeout)+" seconds")
        try:
            return self._task_queue[type].get(block=block,
                                              timeout=timeout)
        except Queue.Empty:
            return None

    def get_tasks(self, type_block_timeout_list):
        if self._verbose:
           print("Received request to get tasks in bulk. "
                 "Queue request types="+str(type_block_timeout_list))

        ret = {}
        for type, block, timeout in type_block_timeout_list:
            task_list = []
            try:
                task_list.append(self._task_queue[type].get(block=block,
                                                            timeout=timeout))
            except Queue.Empty:
                pass
            else:
                while self._task_queue[type].qsize():
                    try:
                        task_list.append(self._task_queue[type].get(block=block,
                                                                    timeout=timeout))
                    except Queue.Empty:
                        pass
            if len(task_list) > 0:
                ret.setdefault(type, []).extend(task_list)

        return ret

    @oneway
    def add_result(self, result, type=None):
        if self._verbose:
           print("Received request to add result with "
                 "result="+str(result)+"; queue type="+str(type))
        self._result_queue[type].put(result)

    # process a set of results in one shot - the input
    # is a dictionary from queue type (including None)
    # to a list of results to be added to that queue.
    @oneway
    def add_results(self, results):
        if self._verbose:
           print("Received request to add bulk result set")
        for result_type in results:
            result_queue = self._result_queue[result_type]
            for result in results[result_type]:
                result_queue.put(result)

    def get_result(self, type=None, block=True, timeout=5):
        if self._verbose:
           print("Received request to get a result from "
                 "queue type="+str(type)+"; block="+str(block)+
                 "; timeout="+str(timeout))
        try:
            return self._result_queue[type].get(block=block,
                                                timeout=timeout)
        except Queue.Empty:
            return None

    def get_results(self, type_block_timeout_list):
        if self._verbose:
           print("Received request to get results in bulk. "
                 "Queue request types="+str(type_block_timeout_list))

        ret = {}
        for type_name, block, timeout in type_block_timeout_list:
            result_list = []
            try:
                result_list.append(self._result_queue[type_name].get(block=block,
                                                                     timeout=timeout))
            except Queue.Empty:
                pass
            else:
                while self._result_queue[type_name].qsize():
                    try:
                        result_list.append(
                            self._result_queue[type_name].get(block=block,
                                                              timeout=timeout))
                    except Queue.Empty:
                        pass
            if len(result_list) > 0:
                ret.setdefault(type_name, []).extend(result_list)

        return ret

    def num_tasks(self, type=None):
        if self._verbose:
           print("Received request for number of tasks in "
                 "queue with type="+str(type))
        return self._task_queue[type].qsize()

    def num_results(self, type=None):
        if self._verbose:
           print("Received request for number of results in "
                 "queue with type="+str(type))
        return self._result_queue[type].qsize()

    def queues_with_results(self):
        if self._verbose:
           print("Received request for the set of queues with results")

        results = []
        #
        # Iterate over a copy of the contents of the queue, since
        # the queue may change while iterating.
        #
        for queue_name, result_queue in list(self._result_queue.items()):
           if result_queue.qsize() > 0:
               results.append(queue_name)

        return results

    def get_results_all_queues(self):

        if self._verbose:
           print("Received request to obtain all available "
                 "results from all queues")

        results = []
        #
        # Iterate over a copy of the contents of the queue, since
        # the queue may change while iterating.
        #
        for queue_name, result_queue in list(self._result_queue.items()):
            while result_queue.qsize() > 0:
                try:
                    results.append(result_queue.get(block=False, timeout=0))
                except Queue.Empty:
                    pass
        return results


def DispatcherServer(group=":PyUtilibServer",
                     host=None,
                     verbose=False,
                     max_allowed_connections=None,
                     worker_limit=None,
                     clear_group=True):

    set_maxconnections(max_allowed_connections=max_allowed_connections)

    #
    # main program
    #
    ns = get_nameserver(host,caller_name="Dispatcher")

    if clear_group:
        for name, uri in get_dispatchers(group=group, ns=ns):
            print("Multiple dispatchers not allowed.")
            print("dispatch_srvr is shutting down...")
            return 1

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
            ns.createGroup(group+".dispatcher")
        except _pyro.errors.NamingError:
            pass
        if clear_group:
            try:
                ns.unregister(group+".dispatcher")
            except _pyro.errors.NamingError:
                pass
    else:
        if clear_group:
            try:
                ns.remove(group+".dispatcher")
            except _pyro.errors.NamingError:
                pass

    disp = Dispatcher(verbose=verbose,
                      worker_limit=worker_limit)
    proxy_name = group+".dispatcher."+str(uuid.uuid4())
    if using_pyro3:
        uri = daemon.connect(disp, proxy_name)
    else:
        uri = daemon.register(disp, proxy_name)
        ns.register(proxy_name, uri)

    # There is no need to retain the proxy connection to the
    # nameserver, so free up resources on the nameserver thread
    if using_pyro4:
        ns._pyroRelease()
    else:
        ns._release()

    print("Dispatcher is ready.")
    return daemon.requestLoop()
