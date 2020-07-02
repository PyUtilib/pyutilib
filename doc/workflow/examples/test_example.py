# Imports
import pyutilib.th as unittest
import glob
import os
from os.path import dirname, abspath, abspath, basename
import sys

currdir = dirname(abspath(__file__))+os.sep
datadir = currdir

def filter(line):
    return 'Running' in line or "IGNORE" in line or line.startswith('usage:') or 'Sub-commands' in line

# Declare an empty TestCase class
class Test(unittest.TestCase):
    pass

# Find all example*.py files, and use them to define baseline tests
for file in glob.glob(datadir+'example*.py'):
    bname = basename(file)
    name=bname.split('.')[0]
    #
    # We use add_baseline_test instead of add_import_test because the latter does not seem to
    # work when running with nosetests
    #
    if not os.path.exists(datadir+name+'.txt'):
        sys.stderr.write("WARNING:  no baseline available for file "+file)
    else:
        Test.add_import_test(name=name, cwd=datadir, baseline=datadir+name+'.txt', filter=filter)

if not sys.platform.startswith('win'):
    # Find all *.sh files, and use them to define baseline tests
    for file in glob.glob(datadir+'*.sh'):
        bname = basename(file)
        name=bname.split('.')[0]
        Test.add_baseline_test(cmd='cd %s; /usr/bin/env bash %s' % (datadir, file),  baseline=datadir+name+'.txt', name=name, filter=filter)

# Execute the tests
if __name__ == '__main__':
    unittest.main()
