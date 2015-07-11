#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________
#

__test__=False

import pyutilib.component.core
pyutilib.component.core.PluginGlobals.add_env('pyutilib.autotest')

from pyutilib.autotest.plugins import *
import pyutilib.autotest.yaml_plugin
import pyutilib.autotest.json_plugin
from pyutilib.autotest.driver import *
import pyutilib.autotest.default_testdriver

pyutilib.component.core.PluginGlobals.pop_env()
