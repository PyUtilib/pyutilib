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
import os, socket, time
import itertools

from pyutilib.pyro import get_nameserver, using_pyro3, using_pyro4
from pyutilib.pyro import Pyro as _pyro
if sys.version_info >= (3,0):
    xrange = range
    import queue as Queue
else:
    import Queue

from six import advance_iterator

class TaskWorkerBase(object):

    def __init__(self,
                 group=":PyUtilibServer",
                 host=None,
                 num_dispatcher_tries=15):

        if _pyro is None:
            raise ImportError("Pyro or Pyro4 is not available")

        # Deprecated in Pyro3
        # Removed in Pyro4
        if using_pyro3:
            _pyro.core.initClient()

        self.ns = get_nameserver(host)
        if self.ns is None:
            raise RuntimeError("TaskWorkerBase failed to locate "
                               "Pyro name server on the network!")
        print('Attempting to find Pyro dispatcher object...')
        URI = None
        for i in xrange(0,num_dispatcher_tries):
            try:
                if using_pyro3:
                    URI = self.ns.resolve(group+".dispatcher")
                else:
                    URI = self.ns.lookup(group+".dispatcher")
                print('Dispatcher Object URI:'+str(URI))
                break
            except _pyro.errors.NamingError:
                pass
            time.sleep(1)
            print("Failed to find dispatcher object from name server - trying again.")
        if URI is None:
            print('Could not find dispatcher object, nameserver says:'+str(x))
            raise SystemExit
        if using_pyro3:
            self.dispatcher = _pyro.core.getProxyForURI(URI)
        else:
            self.dispatcher = _pyro.Proxy(URI)
        self.WORKERNAME = "Worker_%d@%s" % (os.getpid(), socket.gethostname())
        print("This is worker "+self.WORKERNAME)

        # There is no need to retain the proxy connection to the
        # nameserver, so free up resources on the nameserver thread
        if using_pyro4:
            self.ns._pyroRelease()

    def _get_request_type(self):
        raise NotImplementedError("This is an abstract method")

    def run(self):

        print("Listening for work from dispatcher...")

        if using_pyro3:
            connection_problem = _pyro.errors.ConnectionDeniedError
        else:
            connection_problem = _pyro.errors.TimeoutError
        while 1:
            current_type, blocking, timeout = self._get_request_type()
            try:
                task = self.dispatcher.get_task(type=current_type,
                                                block=blocking,
                                                timeout=timeout)
            except connection_problem as e:
                x = sys.exc_info()[1]
                # this can happen if the dispatcher is overloaded
                print("***WARNING: Connection to dispatcher server "
                      "denied\n - exception type: "+str(type(e))+
                      "\n - message: "+str(x))
                if using_pyro3:
                    print("A potential remedy may be to "
                          "increase PYRO_MAXCONNECTIONS from its current "
                          "value of "+str(_pyro.config.PYRO_MAXCONNECTIONS))
                time.sleep(0.1) # sleep for a bit longer than normal, for obvious reasons
            else:
                if task is not None:

                    task['result'] = self.process(task['data'])

                    if task['generateResponse']:
                        task['processedBy'] = self.WORKERNAME
                        self.dispatcher.add_result(task, type=current_type)

                    # give the dispatch server a bit of time to recover
                    # and process the request - it is very unlikely
                    # that it can have another task ready (at least in
                    # most job distribution structures) right away.

                    # TBD: We really need to parameterize the time-out value.
                    time.sleep(0.01)

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
        # **NOTE: For this class type is tuple (type,blocking,timeout)
        #
        self._num_types = 0
        self._type_cycle = None
        self.push_request_type(type_default,block_default,timeout_default)

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

    def num_request_types(self):
        return self._num_types

    def clear_request_types(self):
        self._type_cycle = itertools.cycle([])
        self._num_types = 0

    def push_request_type(self,type,block,timeout):
        """
        add a request type to the end relative to the current cycle
        location
        """
        self._type_cycle = itertools.cycle(self.current_type_order() + \
                                           [(type,block,timeout)])
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
