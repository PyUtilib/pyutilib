#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

import gc

# PauseGC is a class for clean, scoped management of the Python
# garbage collector.  To disable the GC for the duration of a
# function/method, simply:
#
# def my_func():
#    suspend_gc = PauseGC()
#    # [...]
#
# When the function falls out of scope (by termination or exception),
# the GC will be re-enabled.  It is safe to nest instances of PauseGC
# (that is, you don't have to worry if an outer function/method has its
# own instance of PauseGC)
class PauseGC(object):
    __slots__ = ( "reenable_gc" )

    def __init__(self):
        self.reenable_gc = gc.isenabled()
        gc.disable()

    def __del__(self):
        if self.reenable_gc:
            gc.enable()
