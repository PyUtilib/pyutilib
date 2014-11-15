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
from pyutilib.pyro.util import *
import Queue
import Pyro.core
from Pyro.errors import NamingError

if sys.version_info >= (3,0):
    xrange = range


class Client(object):

    def __init__(self, group=":PyUtilibServer", type=None, host=None, num_dispatcher_tries=15):
        self.type=type
        self.id = 0
        Pyro.core.initClient()
        self.ns = get_nameserver(host)
        self.dispatcher = None
        if self.ns is None:
            raise RuntimeError("Client failed to locate Pyro name server on the network!")
        print('Attempting to find Pyro dispatcher object...')
        self.URI = None
        for i in xrange(0,num_dispatcher_tries):
            try:
                self.URI=self.ns.resolve(group+".dispatcher")
                print("Dispatcher Object URI: "+str(self.URI))
                break
            except NamingError:
                pass
            time.sleep(1)
            print("Failed to find dispatcher object from name server - trying again.")
        if self.URI is None:
            print('Could not find dispatcher object, nameserver says:'+str(x))
            raise SystemExit
        self.set_group(group)
        self.CLIENTNAME = "%d@%s" % (os.getpid(), socket.gethostname())
        print("This is client "+self.CLIENTNAME)

    def set_group(self, group):
        self.dispatcher = Pyro.core.getProxyForURI(self.URI)

    def clear_queue(self, override_type=None, verbose=False):
        task_type = override_type if (override_type is not None) else self.type
        if verbose is True:
            print("Clearing all tasks and results for "
                  "type="+str(task_type))
        self.dispatcher.clear_queue(type=task_type)

    def add_task(self, task, override_type=None, verbose=False):
        task_type = override_type if (override_type is not None) else self.type
        if task.id is None:
            task.id = self.CLIENTNAME + "_" + str(self.id)
            self.id += 1
        else:
            task.id = self.CLIENTNAME + "_" + str(task.id)
        if verbose is True:
            print("Adding task "+str(task.id)+" to dispatcher "
                  "queue with type="+str(task_type))
        self.dispatcher.add_task(task, type=task_type)

    def get_result(self, override_type=None, block=True, timeout=5):
        task_type = override_type if (override_type is not None) else self.type
        try:
            return self.dispatcher.get_result(type=task_type, block=block, timeout=timeout)
        except Queue.Empty:
            return None

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
