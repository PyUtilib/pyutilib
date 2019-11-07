# -*- coding: utf-8 -*-

# enum.py
# Part of enum, a package providing enumerated types for Python.
#
# Copyright © 2007 Ben Finney
# This is free software; you may copy, modify and/or distribute this work
# under the terms of the GNU General Public License, version 2 or later
# or, at your option, the terms of the Python license.
#
#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________
#
# William Hart
# Edits to the PyPI enum package to support __call__ and pickling.
#
""" Robust enumerated type support in Python.

This package provides a module for robust enumerations in Python.

An enumeration object is created with a sequence of string arguments
to the Enum() constructor::

    >>> from enum import Enum
    >>> Colours = Enum('red', 'blue', 'green')
    >>> Weekdays = Enum('mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun')

The return value is an immutable sequence object with a value for each
of the string arguments. Each value is also available as an attribute
named from the corresponding string argument::

    >>> pizza_night = Weekdays[4]
    >>> shirt_colour = Colours.green

The values are constants that can be compared only with values from
the same enumeration; comparison with other values will invoke
Python's fallback comparisons::

    >>> pizza_night == Weekdays.fri
    True
    >>> shirt_colour > Colours.red
    True
    >>> shirt_colour == "green"
    False

Each value from an enumeration exports its sequence index
as an integer, and can be coerced to a simple string matching the
original arguments used to create the enumeration::

    >>> str(pizza_night)
    'fri'
    >>> shirt_colour.index
    2
"""

import six


class EnumException(Exception):
    """ Base class for all exceptions in this module. """

    def __init__(self):
        if self.__class__ is EnumException:
            raise NotImplementedError("%s is an abstract class for subclassing"
                                      % self.__class__)


class EnumEmptyError(AssertionError, EnumException):
    """ Raised when attempting to create an empty enumeration. """

    def __str__(self):
        return "Enumerations cannot be empty"


class EnumBadKeyError(TypeError, EnumException):
    """ Raised when creating an Enum with non-string keys. """

    def __init__(self, key):
        self.key = key

    def __str__(self):
        return ("Enumeration keys must be strings or "
                "instances of EnumValue: %s" % (self.key,))


class EnumBadIndexError(AssertionError, EnumException):
    """ Raised when creating an Enum with with an invalid index."""

    def __init__(self, index, reason):
        self.index = index
        self.reason = reason

    def __str__(self):
        return ("Enumeration index (%s) is not valid. Reason: %s" %
                (self.index, self.reason))


class EnumBadTypeError(TypeError, EnumException):
    """ Raised when creating an Enum with a bad type value."""

    def __init__(self, type_, reason):
        self.type_ = type_
        self.reason = reason

    def __str__(self):
        return ("Enumeration type=%r is not valid. Reason: %s" %
                (self.type_, self.reason))


class EnumImmutableError(TypeError, EnumException):
    """ Raised when attempting to modify an Enum. """

    def __init__(self, *args):
        self.args = args

    def __str__(self):
        return "Enumeration does not allow modification"


class EnumValue(object):
    """ A specific value of an enumerated type. """

    def __init__(self, enumtype, index, key):
        """ Set up a new instance. """
        self.__enumtype = enumtype
        self.__index = index
        self.__key = key

    def __get_enumtype(self):
        return self.__enumtype

    enumtype = property(__get_enumtype)

    def __get_key(self):
        return self.__key

    key = property(__get_key)

    def __str__(self):
        return "%s" % (self.key)

    def __get_index(self):
        return self.__index

    index = property(__get_index)

    def __repr__(self):
        return "EnumValue(%s, %s, %s)" % (repr(self.__enumtype),
                                          repr(self.__index),
                                          repr(self.__key),)

    def __hash__(self):
        return hash(self.__index)

    def __lt__(self, other):
        """Less than operator

        (Called in response to 'self < other' or 'other > self'.)
        """
        try:
            return self.index < other.index
        except Exception:
            return NotImplemented

    def __gt__(self, other):
        """Greater than operator

        (Called in response to 'self > other' or 'other < self'.)
        """
        try:
            return self.index > other.index
        except Exception:
            return NotImplemented

    def __le__(self, other):
        """Less than or equal operator

        (Called in response to 'self <= other' or 'other >= self'.)
        """
        try:
            return self.index <= other.index
        except Exception:
            return NotImplemented

    def __ge__(self, other):
        """Greater than or equal operator

        (Called in response to 'self >= other' or 'other <= self'.)
        """
        try:
            return self.index >= other.index
        except Exception:
            return NotImplemented

    def __eq__(self, other):
        """Equal to operator

        (Called in response to 'self == other'.)
        """
        try:
            return self.index == other.index
        except Exception:
            return NotImplemented

    def __ne__(self, other):
        """Equal to operator

        (Called in response to 'self != other'.)
        """
        try:
            return self.index != other.index
        except Exception:
            return NotImplemented


class Enum(object):
    """ Enumerated type. """

    def __init__(self, *keys, **kwargs):
        """ Create an enumeration instance. """

        if not keys:
            raise EnumEmptyError()

        keys = tuple(keys)
        values = [None] * len(keys)

        value_type = kwargs.get('value_type', EnumValue)

        for i, key in enumerate(keys):
            if isinstance(key, six.string_types):
                value = value_type(self, i, key)
            else:
                if not isinstance(key, EnumValue):
                    raise EnumBadKeyError(key)
                value = key
                key = value.key
                if value.index != i:
                    raise EnumBadIndexError(
                        value.index, "Assigned index for argument with key %s, "
                        "does not match location in the initialization list" %
                        (key))
            values[i] = value
            if value.enumtype != values[0].enumtype:
                raise EnumBadTypeError(
                    value.enumtype,
                    "Type assigned to positional argument %s (key=%s) "
                    "does not match the type assigned to the first "
                    "positional argument (key=%s): %r" %
                    (i, key, values[0].key, values[0].enumtype))
            try:
                super(Enum, self).__setattr__(key, value)
            except TypeError:
                raise EnumBadKeyError(key)

        super(Enum, self).__setattr__('_keys', keys)
        super(Enum, self).__setattr__('_values', values)

    def __call__(self, index):
        #
        # If the index is an integer, get the item
        # with this index
        #
        if isinstance(index, int):
            return self[index]
        #
        # If the index is not a string, then try coercing it
        #
        if not isinstance(index, six.string_types):
            tmp = str(index)
        else:
            tmp = index
        return getattr(self, tmp)

    def __setattr__(self, name, value):
        raise EnumImmutableError(name)

    def __delattr__(self, name):
        raise EnumImmutableError(name)

    def __len__(self):
        return len(self._values)

    def __getitem__(self, index):
        return self._values[index]

    def __setitem__(self, index, value):
        raise EnumImmutableError(index)

    def __delitem__(self, index):
        raise EnumImmutableError(index)

    def __iter__(self):
        return iter(self._values)

    def __contains__(self, value):
        is_member = False
        if isinstance(value, six.string_types):
            is_member = (value in self._keys)
        else:
            try:
                is_member = (value in self._values)
            except Exception:
                is_member = False
        return is_member
