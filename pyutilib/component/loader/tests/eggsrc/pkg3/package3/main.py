from pyutilib.component.core import *


class IPackage3Util(Interface):
    """Interface for Package3 utilities"""


class Package3Util(Plugin):

    implements(IPackage3Util)


inst1 = Package3Util()
inst2 = Package3Util()
