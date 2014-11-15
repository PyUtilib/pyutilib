#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

__all__ = ['Connector', 'DirectConnector']


class Connector(object):

    def __init__(self, from_port=None, to_port=None):
        """Constructor."""
        from pyutilib.workflow import task
        if from_port is None:
            self.from_port = task.NoTask         #pragma:nocover
        else:
            self.from_port = from_port
        if to_port is None:
            self.to_port = task.NoTask           #pragma:nocover
        else:
            self.to_port = to_port
 
    def get_value(self):
        raise ValueError("There is no value to get in an abstract Connector object!")  #pragma:nocover

    def ready(self):
        return self.from_port.ready()

    def __repr__(self):
        """Return a string representation for this connection."""
        return str(self)

    def __str__(self):
        """Return a string representation for this connection."""
        return "%s: from=(%s) to=(%s) %s" % (str(self.__class__.__name__), str(self.from_port.task().id), str(self.to_port.task().id), self.ready())


#class UnknownConnector(Connector):

#    def __init__(self, from_port=None, to_port=None):
#        Connector.__init__(self, from_port=from_port, to_port=to_port)


class DirectConnector(Connector):

    def __init__(self, from_port=None, to_port=None):
        Connector.__init__(self, from_port=from_port, to_port=to_port)

    def get_value(self):
        if self.ready():
            return self.from_port.get_value()
        return None

