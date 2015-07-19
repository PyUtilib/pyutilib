#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

#
# Task returns a native Python data type.  This provides more 
# more flexibility in the choice of serialization schemes than 
# a user-defined class.  Also, the default serializer used by Pyro4 
# ('serpent') does not support most user defined classes. The
# serializer can be set to 'pickle' by the user if they need
# this functionality (see: Pyro4 docs).
#
def Task(id=None, data=None, generateResponse=True):
    return {'id': id,
            'data': data,
            'generateResponse': generateResponse,
            'result': None,
            'processedBy': None,
            'type': None}

