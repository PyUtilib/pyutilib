#
# This generates a load error
#
from pyutilib.component.core import *
from pyutilib.component.config import *

class test3_foo(Plugin):

    abc = Option("ABC")

inst = test3_foo()
