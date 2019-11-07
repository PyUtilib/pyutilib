from pyutilib.component.core import *


class IPackage5Util(Interface):
    """Interface for Package5 utilities"""


class Package5Util(SingletonPlugin):

    implements(IPackage5Util)
