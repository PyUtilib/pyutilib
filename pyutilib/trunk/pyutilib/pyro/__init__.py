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

# For now, default to using Pyro3 if available
# otherwise, check for Pyro4
Pyro = None
using_pyro3 = False
using_pyro4 = False
try:
    import Pyro
    import Pyro.core
    import Pyro.naming
    using_pyro3 = True
    using_pyro4 = False
except:
    try:
        import Pyro4
        #Pyro4.config.SERIALIZERS_ACCEPTED.add('pickle')
        #Pyro4.config.SERIALIZER = 'pickle'
        Pyro = Pyro4
        using_pyro3 = False
        using_pyro4 = True
    except:
        Pyro = None
        using_pyro3 = False
        using_pyro4 = False

from pyutilib.pyro.util import *
from pyutilib.pyro.task import *
from pyutilib.pyro.client import *
from pyutilib.pyro.worker import *
from pyutilib.pyro.dispatcher import *
from pyutilib.pyro.nameserver import *

#
# Pyro3 License
#

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


#
# Pyro4 License
#

#
#Pyro - Python Remote Objects
#Software License, copyright, and disclaimer
#
#  Pyro is Copyright (c) by Irmen de Jong (irmen@razorvine.net).
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
#
#
#This is the "MIT Software License" which is OSI-certified, and GPL-compatible.
#See http://www.opensource.org/licenses/mit-license.php
