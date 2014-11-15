import pyutilib.misc
import pyutilib.component.core
import os
import sys

currdir=sys.argv[-1]+os.sep

pyutilib.component.core.PluginGlobals.env().load_services(path=[currdir+"plugins1", currdir+"plugins2"], auto_disable=True)
pyutilib.misc.setup_redirect(currdir+"load2a.out")
pyutilib.component.core.PluginGlobals.pprint(plugins=False, show_ids=False)
pyutilib.misc.reset_redirect()
#pyutilib.component.core.PluginGlobals.pprint()
