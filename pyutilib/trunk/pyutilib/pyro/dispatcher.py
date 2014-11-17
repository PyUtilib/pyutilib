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

from pyutilib.pyro import get_nameserver, using_pyro3, using_pyro4
from pyutilib.pyro import Pyro as _pyro
if sys.version_info >= (3,0):
    import queue as Queue
else:
    import Queue

if using_pyro3:
    base = _pyro.core.ObjBase
else:
    base = object
class Dispatcher(base):

    def __init__(self, **kwds):
        if _pyro is None:
            raise ImportError("Pyro or Pyro4 is not available")
        if using_pyro3:
            _pyro.core.ObjBase.__init__(self)
        else:
            self._pyroOneway = set('shutdown')
        self.default_task_queue = Queue.Queue()
        self.default_result_queue = Queue.Queue()
        self.task_queue = {}
        self.result_queue = {}
        self.verbose = kwds.get("verbose", False)
        if self.verbose:
           print("Verbose output enabled...")

    def shutdown(self):
        print("Dispatcher received request to shut down - initiating...")
        if using_pyro3:
            self.getDaemon().shutdown()
        else:
            self._pyroDaemon.shutdown()

    def clear_queue(self, type=None):
        if type is None:
            self.default_task_queue = Queue.Queue()
            self.default_result_queue = Queue.Queue()
        else:
            if type in self.task_queue:
                del self.task_queue[type]
            if type in self.result_queue:
                del self.result_queue[type]

    def add_task(self, task, type=None):
        if self.verbose:
           print("Received request to add task=<Task id="
                 +str(task['id'])+">; queue type="+str(type))
        if type is None:
            self.default_task_queue.put(task)
        else:
            if not type in self.task_queue:
                self.task_queue[type] = Queue.Queue()
            self.task_queue[type].put(task)

    def get_task(self, type=None, block=True, timeout=5):
        if self.verbose:
           print("Received request to get a task from "
                 "queue type="+str(type)+"; block="+str(block)+
                 "; timeout="+str(timeout)+" seconds")
        try:
            if type is None:
                return self.default_task_queue.get(block=block, timeout=timeout)
            else:
                if not type in self.task_queue:
                    self.task_queue[type] = Queue.Queue()
                return self.task_queue[type].get(block=block, timeout=timeout)
        except Queue.Empty:
            return None

    def add_result(self, data, type=None):
        if self.verbose:
           print("Received request to add result with "
                 "data="+str(data)+"; queue type="+str(type))
        if type is None:
            self.default_result_queue.put(data)
        else:
            if not type in self.result_queue:
                self.result_queue[type] = Queue.Queue()
            self.result_queue[type].put(data)

    def get_result(self, type=None, block=True, timeout=5):
        if self.verbose:
           print("Received request to get a result from "
                 "queue type="+str(type)+"; block="+str(block)+
                 "; timeout="+str(timeout))
        try:
            if type is None:
                return self.default_result_queue.get(block=block, timeout=timeout)
            else:
                if not type in self.result_queue:
                    self.result_queue[type] = Queue.Queue()
                return self.result_queue[type].get(block=block, timeout=timeout)
        except Queue.Empty:
            return None

    def num_tasks(self, type=None):
        if self.verbose:
           print("Received request for number of tasks in "
                 "queue with type="+str(type))
        if type is None:
            return self.default_task_queue.qsize()
        elif type in self.task_queue:
            return self.task_queue[type].qsize()
        return 0

    def num_results(self, type=None):
        if self.verbose:
           print("Received request for number of results in "
                 "queue with type="+str(type))
        if type is None:
            return self.default_result_queue.qsize()
        elif type in self.result_queue:
            return self.result_queue[type].qsize()
        return 0

    def queues_with_results(self):
        if self.verbose:
           print("Received request for the set of queues with results")
        result = set()
        if self.default_result_queue.qsize() > 0:
            result.add(None)

        # IMPORTANT: Make sure to make a copy (via the items() call)
        #            of the queue contents - it can change
        #            mid-iteration, due to the introduction of new
        #            named queues.
        #
        # *python3 fix: items() no longer copies, so was changed to
        # *list(items())
        #

        for queue_name, result_queue in list(self.result_queue.items()):
           if result_queue.qsize() > 0:
               result.add(queue_name)
        return result

    def get_results_all_queues(self):

        if self.verbose:
           print("Received request to obtain all available results from all queues")

        result = []

        while self.default_result_queue.qsize() > 0:
            try:
                result.append(self.default_result_queue.get(block=False))
            except Queue.Empty:
                pass

        # IMPORTANT: Make sure to make a copy (via the items() call)
        #            of the queue contents - it can change
        #            mid-iteration, due to the introduction of new
        #            named queues.
        #
        # *python3 fix: items() no longer copies, so was changed to
        # *list(items())
        #

        for queue_name, result_queue in list(self.result_queue.items()):

            while result_queue.qsize() > 0:
                try:
                    result.append(result_queue.get(block=False, timeout=0))
                except Queue.Empty:
                    pass

        return result

def DispatcherServer(group=":PyUtilibServer", host=None, verbose=False):

    max_pyro_connections_envname = "MAX_PYRO_CONNECTIONS"
    if max_pyro_connections_envname in os.environ:
        if using_pyro3:
            new_val = int(os.environ[max_pyro_connections_envname])
            print("Setting maximum number of connections to dispatcher to "
                  +str(new_val)+", based on specification provided by "
                  +max_pyro_connections_envname+" environment variable")
            _pyro.config.PYRO_MAXCONNECTIONS = new_val
        else:
            print("Setting maximum number of connections to dispatcher "
                  "is not allowed with Pyro4. "+max_pyro_connections_envname
                  +" environment variable will be ignored.")
    elif using_pyro3:
        # the default value is rather small, so we'll use something a
        # bit more reasonable.
        _pyro.config.PYRO_MAXCONNECTIONS = 1000

    #
    # main program
    #
    ns = get_nameserver(host)
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

    print("Dispatcher is ready.")
    daemon.requestLoop()
