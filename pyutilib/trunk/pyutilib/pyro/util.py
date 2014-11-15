#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

__all__ = ['get_nameserver']

import os
import time
import random
import Pyro.core
import Pyro.naming
from Pyro.errors import NamingError, ConnectionDeniedError

def get_nameserver(host=None, num_retries=30):

    timeout_upper_bound = 5.0

    if not host is None:
        os.environ['PYRO_NS_HOSTNAME'] = host
    elif 'PYRO_NS_HOSTNAME' in os.environ:
        host = os.environ['PYRO_NS_HOSTNAME']

    Pyro.core.initServer()

    ns = None

    for i in xrange(0, num_retries):
        try:
            if host is None:
                ns=Pyro.naming.NameServerLocator().getNS()
            else:
                ns=Pyro.naming.NameServerLocator().getNS(host)
            break
        except NamingError:
            pass
        except ConnectionDeniedError:
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
