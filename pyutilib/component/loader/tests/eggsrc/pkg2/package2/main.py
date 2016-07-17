from pyutilib.component.core import *


class IPackage2Util(Interface):
    """Interface for Package2 utilities"""


class Package2Util(Plugin):

    implements(IPackage1Util)
