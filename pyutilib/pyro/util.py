#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

__all__ = ['get_nameserver','shutdown_pyro_components']

import os
import sys
import time
import random

from pyutilib.pyro import using_pyro3, using_pyro4
from pyutilib.pyro import Pyro as _pyro
if sys.version_info >= (3,0):
    xrange = range
    import queue as Queue
else:
    import Queue

def get_nameserver(host=None, num_retries=30):

    if _pyro is None:
        raise ImportError("Pyro or Pyro4 is not available")

    timeout_upper_bound = 5.0

    if not host is None:
        os.environ['PYRO_NS_HOSTNAME'] = host
    elif 'PYRO_NS_HOSTNAME' in os.environ:
        host = os.environ['PYRO_NS_HOSTNAME']

    # Deprecated in Pyro3
    # Removed in Pyro4
    if using_pyro3:
        _pyro.core.initServer()

    ns = None

    if using_pyro3:
        connection_problem = _pyro.errors.ConnectionDeniedError
    else:
        connection_problem = _pyro.errors.TimeoutError
    for i in xrange(0, num_retries):
        try:
            if using_pyro3:
                if host is None:
                    ns = _pyro.naming.NameServerLocator().getNS()
                else:
                    ns = _pyro.naming.NameServerLocator().getNS(host)
            else:
                ns = _pyro.locateNS(host=host)
            break
        except _pyro.errors.NamingError:
            pass
        except connection_problem:
            # this can occur if the server is too busy.
            pass

        # we originally had a single sleep timeout value, hardcoded to 1 second.
        # the problem with this approach is that if a large number of concurrent
        # processes fail, then they will all re-attempt at roughly the same
        # time. causing more contention than is necessary / desirable. by randomizing
        # the sleep interval, we are hoping to distribute the number of clients
        # attempting to connect to the name server at any given time.
        # TBD: we should eventually read the timeout upper bound from an enviornment
        #      variable - to support cases with a very large (hundreds to thousands)
        #      number of clients.
        sleep_interval = random.uniform(1.0, timeout_upper_bound)
        print("Failed to locate nameserver - trying again in %5.2f seconds." % sleep_interval)
        time.sleep(sleep_interval)

    if ns is None:
        print("Could not locate nameserver after "+str(num_retries)+" attempts.")
        raise SystemExit

    return ns

#
# a utility for shutting down Pyro-related components, which at the
# moment is restricted to the name server and any dispatchers. the
# mip servers will come down once their dispatcher is shut down.
# NOTE: this is a utility that should eventually become part of
#       pyutilib.pyro, but because is prototype, I'm keeping it
#       here for now.
#

def shutdown_pyro_components(host=None, num_retries=30):

    if _pyro is None:
        raise ImportError("Pyro or Pyro4 is not available")

    ns = get_nameserver(host=host, num_retries=num_retries)
    if ns is None:
        print("***WARNING - Could not locate name server "
              "- Pyro PySP components will not be shut down")
        return

    if using_pyro3:
        ns_entries = ns.flatlist()
        for (name,uri) in ns_entries:
            if name == ":Pyro.NameServer":
                proxy = _pyro.core.getProxyForURI(uri)
                proxy._shutdown()
            elif name == ":PyUtilibServer.dispatcher":
                proxy = _pyro.core.getProxyForURI(uri)
                proxy.shutdown()
    elif using_pyro4:
        ns_entries = ns.list()
        for name in ns_entries:
            if name == ":PyUtilibServer.dispatcher":
                URI = ns.lookup(name)
                proxy = _pyro.Proxy(URI)
                proxy.shutdown()
                proxy._pyroRelease()
        print("")
        print("*** NameServer must be shutdown manually when using Pyro4 ***")
        print("")
