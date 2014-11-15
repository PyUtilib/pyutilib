# Imports
import pyutilib.th as unittest
import os
from os.path import dirname, abspath, abspath, basename
import sys

currdir = dirname(abspath(__file__))+os.sep
datadir = os.sep.join([dirname(dirname(dirname(dirname(abspath(__file__))))),'doc','workflow','examples'])+os.sep

os.chdir(datadir)
sys.path.insert(0, datadir)

from test_example import *

sys.path.remove(datadir)

# Execute the tests
if __name__ == '__main__':
    unittest.main()
