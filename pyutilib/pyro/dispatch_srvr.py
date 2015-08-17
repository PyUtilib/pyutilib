#!/usr/bin/env python

import sys
from optparse import OptionParser

import pyutilib.pyro
from pyutilib.pyro import Pyro as _pyro

def main():
    parser = OptionParser()
    parser.add_option(
        "--verbose", dest="verbose",
        help="Activate verbose output.",
        action="store_true", default=False)
    parser.add_option(
        "--max-connections", dest="max_connections",
        help=("Set the maximum number of worker connections "
              "allowed on this dispatcher. By default, the environment "
              "variable PYUTILIB_PYRO_MAXCONNECTIONS is used if present; "
              "otherwise, the default settings for Pyro or Pyro4 are used."),
        type="int", default=None)
    parser.add_option(
        "-n", dest="hostname",
        help="Hostname where nameserver can be found",
        default=None)
    parser.add_option(
        "--allow-multiple", dest="allow_multiple",
        help="Allow multiple dispatchers to run under the default nameserver group",
        default=False, action="store_true")

    options, args = parser.parse_args()
    # Handle the old syntax which was purly argument driven
    # e.g., <hostname> <verbose flag>
    verbose = False
    if len(args) == 2:
        host=sys.argv[1]
        if host == "None":
           host=None
        verbose=bool(sys.argv[2])
        print("DEPRECATION WARNING: dispatch_srvr is now option driven (see dispatch_srvr --help)")
    elif len(args) == 1:
        host=sys.argv[1]
        print("DEPRECATION WARNING: dispatch_srvr is now option driven (see dispatch_srvr --help)")
    else:
        host = options.hostname
        verbose = options.verbose

    if _pyro is None:
        raise ImportError("Pyro or Pyro4 is not available")
    pyutilib.pyro.DispatcherServer(host=host,
                                   verbose=verbose,
                                   max_connections=options.max_connections,
                                   clear_group=not options.allow_multiple)

if __name__ == '__main__':
    main()
