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

if 'nose' not in sys.modules and 'nose2' not in sys.modules:
    raise ImportError('pyutilib.enum has been deprecated. Similar functionality '
                      'can be found in the Python enum package')
