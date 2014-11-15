#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

"""
Python modules that use Pyro to manage a generic task queue.

These modules were adapted from Pyro's distributed2 example.
"""

try:
    import Pyro
    pyro_available=True
except:
    pyro_available=False

if pyro_available:
    from task import *
    from client import *
    from worker import *
    from dispatcher import *
    import util

#
#Pyro Software License (MIT license):
#
#Pyro is Copyright (c) by Irmen de Jong.
#
#Permission is hereby granted, free of charge, to any person obtaining a
#copy of this software and associated documentation files (the "Software"),
#to deal in the Software without restriction, including without limitation
#the rights to use, copy, modify, merge, publish, distribute, sublicense,
#and/or sell copies of the Software, and to permit persons to whom the
#Software is furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included
#in all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
#OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#OTHER DEALINGS IN THE SOFTWARE.
#
#This is the "MIT Software License" which is Open
#Source Initiative (OSI) certified, and GPL-compatible.  See
#http://www.opensource.org/licenses/mit-license.php (it strongly resembles
#the modified BSD license).
#
