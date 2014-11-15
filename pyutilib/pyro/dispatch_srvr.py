#!/usr/bin/env python

import sys

try:
    import cPickle as pickle
except ImportError:
    import pickle

import pyutilib.pyro

def main():
    verbose=False
    if (len(sys.argv) is 2) and (sys.argv[1] is "--help"):
       print("Invocation syntax for dispatch_srvr is: dispatch_srvr nameserver-host enable-verbose-output")
       print("The nameserver-host can be None (local). The enable-verbose-output flag can be 1/0 or True/False.")
       sys.exit(0)
    if len(sys.argv) is 3:
        host=sys.argv[1]
        if host == "None":
           host=None
        verbose=bool(sys.argv[2])
    elif len(sys.argv) is 2:
        host=sys.argv[1]
    else:
        host=None
    pyutilib.pyro.DispatcherServer(host=host,verbose=verbose)

if __name__ == '__main__':
    main()
