#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

__all__ = ['infinity', 'nan', 'is_nan', 'is_finite']
"""
Definitions of mathematical constants
"""

import sys
import math

if sys.version_info < (2, 6):
    """ Definition of infinity """
    infinity = float(1e3000)
    """ Definition of NaN """
    nan = infinity / infinity

    def is_nan(x):
        """
        Returns true if the argument is a float and it does not equal itself
        """
        return type(x) is float and x != x

    def is_finite(val):
        """
        Returns true if the argument is a float or int and it is not infinite or NaN
        """
        return type(val) in (float, int) and val not in (infinity, -infinity,
                                                         nan)

else:
    """ Definition of infinity """
    infinity = float('inf')
    """ Definition of NaN """
    nan = infinity / infinity

    def is_nan(x):
        """
        Returns true if the argument is a float and it does not equal itself
        """
        try:
            return math.isnan(x)
        except TypeError:
            return False

    def is_finite(x):
        """
        Returns true if the argument is a float or int and it is not infinite or NaN
        """
        try:
            return not math.isinf(x)
        except TypeError:
            return False
