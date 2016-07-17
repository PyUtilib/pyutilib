import os
from os.path import abspath, dirname
currdir = dirname(abspath(__file__)) + os.sep

import pyutilib.th as unittest


class Tester(unittest.TestCase):

    def test_pass(self):
        pass

    @unittest.expectedFailure
    def test_fail(self):
        self.fail("test_fail will always fail")

    @unittest.skip("demonstrating skipping")
    def test_skip(self):
        self.fail("test_skip will always be skipped")

    def test_data(self):
        self.recordTestData('foo', 'bar')


#@unittest.category('_foo_')
class Tester2(unittest.TestCase):

    def test_pass(self):
        pass


Tester2 = unittest.category('_foo_')(Tester2)

#
# This class will create a test failure when the
# test category is _ignore_.  This is used to validate
# that tests classes will be skipped if another category
# is specified.
#


#@unittest.category('_ignore_')
class Tester3(unittest.TestCase):

    def test_fail(self):
        if os.environ.get('PYUTILIB_UNITTEST_CATEGORIES', '') == '_ignore_':
            self.fail(
                "test_fail will fail when the _ignore_ category is specified.")


Tester3 = unittest.category('_ignore_')(Tester3)

if __name__ == "__main__":
    unittest.main()
