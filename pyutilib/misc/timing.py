#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________
#

import sys
import time
import traceback

__all__ = ('tic', 'toc')

_lastTime = _loadTime = time.time()


def tic(msg=None):
    global _lastTime
    _lastTime = time.time()
    if msg is None:
        msg = "Resetting the tic/toc delta timer"
    if msg:
        toc(msg, False)


def toc(msg=None, delta=True, ostream=None):

    now = time.time()
    if ostream is None:
        ostream = sys.stdout
    if msg is None:
        msg = 'File "%s", line %s in %s' % \
              traceback.extract_stack(limit=2)[0][:3]

    if delta:
        global _lastTime
        ans = now - _lastTime
        ostream.write("[+%7.2f] %s\n" % (ans, msg))
        _lastTime = now
    else:
        ans = now - _loadTime
        ostream.write("[%8.2f] %s\n" % (ans, msg))
    return ans
