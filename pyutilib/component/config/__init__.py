#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

"""
The pyutilib.component.config package includes utilities to configure
the PyUtilib Component Architecture.  This includes facilities for using
configuration files, controlling logging, and specifying component options.
"""

from pyutilib.component.core import PluginGlobals
PluginGlobals.add_env("pca")

from pyutilib.component.config.options import *
from pyutilib.component.config.managed_plugin import *
from pyutilib.component.config.configuration import *
from pyutilib.component.config.logging_config import *
from pyutilib.component.config.env_config import *
from pyutilib.component.config.tempfiles import *
import pyutilib.component.config.plugin_ConfigParser

PluginGlobals.pop_env()
