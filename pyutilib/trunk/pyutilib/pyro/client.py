#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

__all__ = ['Client']

import sys
import os, socket
import time

from pyutilib.pyro import get_nameserver, using_pyro3, using_pyro4
from pyutilib.pyro import Pyro as _pyro
if sys.version_info >= (3,0):
    xrange = range
    import queue as Queue
else:
    import Queue

class Client(object):

    def __init__(self, group=":PyUtilibServer", type=None, host=None, num_dispatcher_tries=15):
        if _pyro is None:
            raise ImportError("Pyro or Pyro4 is not available")
        self.type=type
        self.id = 0

        # Deprecated in Pyro3
        # Removed in Pyro4
        if using_pyro3:
            _pyro.core.initClient()

        self.ns = get_nameserver(host)
        if self.ns is None:
            raise RuntimeError("Client failed to locate Pyro name "
                               "server on the network!")
        self.dispatcher = None
        print('Attempting to find Pyro dispatcher object...')
        self.URI = None
        for i in xrange(0,num_dispatcher_tries):
            try:
                if using_pyro3:
                    self.URI = self.ns.resolve(group+".dispatcher")
                else:
                    self.URI = self.ns.lookup(group+".dispatcher")
                print("Dispatcher Object URI: "+str(self.URI))
                break
            except _pyro.errors.NamingError:
                pass
            time.sleep(1)
            print("Failed to find dispatcher object from name server - trying again.")
        if self.URI is None:
            print('Could not find dispatcher object, nameserver says:'+str(x))
            raise SystemExit
        self.set_group(group)
        self.CLIENTNAME = "%d@%s" % (os.getpid(), socket.gethostname())
        print("This is client "+self.CLIENTNAME)

        # There is no need to retain the proxy connection to the
        # nameserver, so free up resources on the nameserver thread
        if using_pyro4:
            self.ns._pyroRelease()

    def set_group(self, group):
        if using_pyro3:
            self.dispatcher = _pyro.core.getProxyForURI(self.URI)
        else:
            self.dispatcher = _pyro.Proxy(self.URI)

    def clear_queue(self, override_type=None, verbose=False):
        task_type = override_type if (override_type is not None) else self.type
        if verbose:
            print("Clearing all tasks and results for "
                  "type="+str(task_type))
        self.dispatcher.clear_queue(type=task_type)

    def add_task(self, task, override_type=None, verbose=False):
        task_type = override_type if (override_type is not None) else self.type
        if task['id'] is None:
            task['id'] = self.CLIENTNAME + "_" + str(self.id)
            self.id += 1
        else:
            task['id'] = self.CLIENTNAME + "_" + str(task['id'])
        if verbose:
            print("Adding task "+str(task['id'])+" to dispatcher "
                  "queue with type="+str(task_type))
        self.dispatcher.add_task(task, type=task_type)

    def get_result(self, override_type=None, block=True, timeout=5):
        task_type = override_type if (override_type is not None) else self.type
        return self.dispatcher.get_result(type=task_type, block=block, timeout=timeout)

    def get_results_all_queues(self):
        return self.dispatcher.get_results_all_queues()

    def num_tasks(self, override_type=None):
        task_type = override_type if (override_type is not None) else self.type
        return self.dispatcher.num_tasks(type=task_type)

    def num_results(self, override_type=None):
        task_type = override_type if (override_type is not None) else self.type
        return self.dispatcher.num_results(type=override_type)

    def queues_with_results(self):
        return self.dispatcher.queues_with_results()
