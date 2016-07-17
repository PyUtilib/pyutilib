#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

__all__ = ['ExcelSpreadsheet']

import pyutilib.common

#
# Attempt to import openpyxl
#
try:
    import openpyxl
    _openpyxl = True
except:
    _openpyxl = False
#
# Attempt to import xlrd
#
try:
    import xlrd
    _xlrd = True
except:
    _xlrd = False
#
# Attempt to import win32com stuff. 
#
try:
    from win32com.client.dynamic import Dispatch
    from pythoncom import CoInitialize, CoUninitialize
    from pythoncom import CoInitialize, CoUninitialize, com_error
    _win32com = True
except:
    _win32com = False  #pragma:nocover

from pyutilib.excel.base import ExcelSpreadsheet_base

if _win32com:
    from pyutilib.excel.spreadsheet_win32com import ExcelSpreadsheet_win32com
else:

    class ExcelSpreadsheet_win32com(ExcelSpreadsheet_base):
        pass


if _openpyxl:
    from pyutilib.excel.spreadsheet_openpyxl import ExcelSpreadsheet_openpyxl
else:

    class ExcelSpreadsheet_openpyxl(ExcelSpreadsheet_base):
        pass


if _xlrd:
    from pyutilib.excel.spreadsheet_xlrd import ExcelSpreadsheet_xlrd
else:

    class ExcelSpreadsheet_xlrd(ExcelSpreadsheet_base):
        pass


class ExcelSpreadsheet(ExcelSpreadsheet_base):

    def __new__(cls, *args, **kwds):
        #
        # Note that this class returns class instances rather than
        # class types.  This is because these classes are not
        # subclasses of ExcelSpreadsheet, and thus the __init__
        # method will not be called unless we construct the
        # class instances here.
        #
        ctype = kwds.pop('ctype', None)
        if ctype == 'win32com':
            return ExcelSpreadsheet_win32com(*args, **kwds)
        if ctype == 'openpyxl':
            return ExcelSpreadsheet_openpyxl(*args, **kwds)
        if ctype == 'xlrd':
            return ExcelSpreadsheet_xlrd(*args, **kwds)
        #
        if _win32com:
            return ExcelSpreadsheet_win32com(*args, **kwds)
        if _openpyxl:
            return ExcelSpreadsheet_openpyxl(*args, **kwds)
        if _xlrd:
            return ExcelSpreadsheet_xlrd(*args, **kwds)
        #
        return super(ExcelSpreadsheet, cls).__new__(cls)
