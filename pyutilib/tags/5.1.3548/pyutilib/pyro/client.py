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

from six import iteritems

from pyutilib.pyro import get_nameserver, using_pyro3, using_pyro4
from pyutilib.pyro import Pyro as _pyro

if sys.version_info >= (3,0):
    xrange = range
    import queue as Queue
else:
    import Queue


class Client(object):

    def __init__(self, 
                 group=":PyUtilibServer", 
                 type=None, 
                 host=None, 
                 num_dispatcher_tries=30,
                 caller_name = "Client"):
        if _pyro is None:
            raise ImportError("Pyro or Pyro4 is not available")
        self.type=type
        self.id = 0

        # Deprecated in Pyro3
        # Removed in Pyro4
        if using_pyro3:
            _pyro.core.initClient()

        self.ns = get_nameserver(host, caller_name=caller_name)
        if self.ns is None:
            raise RuntimeError("Client failed to locate Pyro name "
                               "server on the network!")
        self.dispatcher = None
        print('Client attempting to find Pyro dispatcher object...')
        self.URI = None
        cumulative_sleep_time = 0.0
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
            sleep_interval = 10.0
            print("Client failed to find dispatcher object from name server after %d attempts and %5.2f seconds - trying again in %5.2f seconds." % (i+1,cumulative_sleep_time,sleep_interval))
            time.sleep(sleep_interval)
            cumulative_sleep_time += sleep_interval
        if self.URI is None:
            print('Client could not find dispatcher object - giving up')
            raise SystemExit
        self.set_group(group)
        self.CLIENTNAME = "%d@%s" % (os.getpid(), socket.gethostname())
        print("Connection to dispatch server established after %d attempts and %5.2f seconds - this is client: %s" % (i+1, cumulative_sleep_time, self.CLIENTNAME))

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

    def add_tasks(self, type_to_task_list_dict, verbose=False):
        for task_type, task_list in iteritems(type_to_task_list_dict):
            for task in task_list:
                if task['id'] is None:
                    task['id'] = self.CLIENTNAME + "_" + str(self.id)
                    self.id += 1
                else:
                    task['id'] = self.CLIENTNAME + "_" + str(task['id'])
            if verbose:
                print("Adding task "+str(task['id'])+" to dispatcher "
                      "queue with type="+str(task_type)+" - in bulk")

        self.dispatcher.add_tasks(type_to_task_list_dict)
                
    def add_task(self, task, override_type=None, verbose=False):
        task_type = override_type if (override_type is not None) else self.type
        if task['id'] is None:
            task['id'] = self.CLIENTNAME + "_" + str(self.id)
            self.id += 1
        else:
            task['id'] = self.CLIENTNAME + "_" + str(task['id'])
        if verbose:
            print("Adding task "+str(task['id'])+" to dispatcher "
                  "queue with type="+str(task_type)+" - individually")
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
