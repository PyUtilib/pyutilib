#
# Plugin load tests, with the sys.path loader disabled.
#

import os
import sys
from os.path import abspath, dirname
currdir = dirname(abspath(__file__))+os.sep

import pyutilib.th as unittest
import pyutilib.subprocess


class Test(unittest.TestCase):

    def test_load1(self):
        pyutilib.subprocess.run(sys.executable+" "+currdir+os.sep+"load1.py "+currdir)
        self.assertMatchesYamlBaseline(currdir+"load1.out", currdir+"load1.txt")

    def test_load1a(self):
        pyutilib.subprocess.run(sys.executable+" "+currdir+os.sep+"load1a.py "+currdir)
        self.assertMatchesYamlBaseline(currdir+"load1a.out", currdir+"load1a.txt")

    def test_load2(self):
        pyutilib.subprocess.run(sys.executable+" "+currdir+os.sep+"load2.py "+currdir)
        self.assertMatchesYamlBaseline(currdir+"load2.out", currdir+"load2.txt")

    def test_load2a(self):
        pyutilib.subprocess.run(sys.executable+" "+currdir+os.sep+"load2a.py "+currdir)
        self.assertMatchesYamlBaseline(currdir+"load2a.out", currdir+"load2a.txt")

if __name__ == "__main__":
    unittest.main()
