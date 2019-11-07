from pyutilib.component.core import *


class IPackage4Util(Interface):
    """Interface for Package4 utilities"""


class Package4Util(SingletonPlugin):

    implements(IPackage4Util)
