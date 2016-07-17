#
# This generates a load error
#
from pyutilib.component.core import Plugin
from pyutilib.component.config import Option


class test3_foo(Plugin):

    abc = Option("ABC")


inst = test3_foo()
