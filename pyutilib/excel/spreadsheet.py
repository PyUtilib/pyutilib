
__all__ = ['ExcelSpreadsheet']

import pyutilib.common

try:
    import xlrd
    _xlrd=True
except:
    _xlrd=False
#
# Attempt to import win32com stuff. 
#
try:
    from win32com.client.dynamic import Dispatch
    from pythoncom import CoInitialize, CoUninitialize
    from pythoncom import CoInitialize, CoUninitialize, com_error
    _win32com=True
except:
    _win32com=False #pragma:nocover

if _xlrd:

    from pyutilib.excel.spreadsheet_xlrd import *

elif _win32com:

    from pyutilib.excel.spreadsheet_win32com import *

else:

    class ExcelSpreadsheet(object):

        def __init__(self, *args, **kwargs):
            raise pyutilib.common.ApplicationError("Cannot dispatch Excel without win32com")


