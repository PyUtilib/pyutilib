from pyutilib.component.core import *


class IPackage7Util(Interface):
    """Interface for Package7 utilities"""


class Package7Util(SingletonPlugin):

    implements(IPackage7Util)
