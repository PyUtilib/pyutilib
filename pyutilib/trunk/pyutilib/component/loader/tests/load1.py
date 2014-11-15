import pyutilib.misc
import pyutilib.component.core
import os
import sys
import logging

currdir=sys.argv[-1]+os.sep

logging.basicConfig(level=logging.DEBUG)
pyutilib.component.core.PluginGlobals.env().load_services(path=currdir+"plugins1")
pyutilib.misc.setup_redirect(currdir+"load1.out")
pyutilib.component.core.PluginGlobals.pprint(plugins=False, show_ids=False)
pyutilib.misc.reset_redirect()
