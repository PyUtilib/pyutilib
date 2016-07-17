import os
from os.path import abspath, dirname
currdir = dirname(abspath(__file__)) + os.sep

import pyutilib.th as unittest

tmp = os.environ.get('PYUTILIB_UNITTEST_CATEGORY', '')
os.environ['PYUTILIB_UNITTEST_CATEGORY'] = '_foo_'


#@unittest.category('_oof_')
class Tester4(unittest.TestCase):

    def test_pass(self):
        self.fail("Should not execute this suite")


Tester4 = unittest.category('_oof_')(Tester4)

os.environ['PYUTILIB_UNITTEST_CATEGORY'] = tmp

if __name__ == "__main__":
    unittest.main()
