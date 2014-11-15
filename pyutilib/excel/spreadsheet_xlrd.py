#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

"""
A class for interacting with an Excel spreadsheet.
"""

#
# Imports
#
import os
import sys

import xlrd


class ExcelSpreadsheet(object):

    xlToLeft = 1
    xlToRight = 2
    xlUp = 3
    xlDown = 4
    xlThick = 4
    xlThin = 2
    xlEdgeBottom=9

    def __init__(self, filename=None, worksheets=(1,), default_worksheet=1):
        """
        Constructor.
        """
        self.wb=None
        self.xlsfile=None
        if filename is not None:
            self.open(filename, worksheets, default_worksheet)

    def open(self, filename, worksheets=(1,), default_worksheet=1):
        """
        Initialize this object from a file.
        """
        #
        # Set the excel spreadsheet name
        #
        if sys.platform.startswith('win') and filename[1] == ":":
            self.xlsfile=filename
        else:
            self.xlsfile=os.path.join(os.getcwd(), filename)
        #
        # Start the excel spreadsheet
        #
        self.wb = xlrd.open_workbook(self.xlsfile)
        self.worksheets=set(worksheets)
        self._ws = {}
        for wsid in worksheets:
            if type(wsid) is int:
                self._ws[wsid] = self.wb.sheet_by_index(wsid)
            else:
                self._ws[wsid] = self.wb.sheet_by_name(wsid)
            #self._ws[wsid].Activate()
        self.default_worksheet=default_worksheet

    def ws(self):
        """ The active worksheet """
        return self._ws[self.default_worksheet]

    def __del__(self):
        """
        Close the spreadsheet when deleting this object.
        """
        self.close()

    def activate(self, name):
        """ Activate a specific sheet """
        if name is None:
            return
        if not name in self._ws:
            self.worksheets.add(name)
            if type(name) is int:
                self._ws[name] = self.wb.sheet_by_index(name)
            else:
                self._ws[name] = self.wb.sheet_by_name(name)
            #self._ws[name].Activate()
        self.default_worksheet=name

    def close(self):
        """
        Close the spreadsheet
        """
        if self is None:       #pragma:nocover
            return
        if self.wb is None:
            return
        self.wb.release_resources()
        self._ws = {}

    def calc_iterations(self, val=None):
        raise ValueError("ExcelSpreadsheet calc_iterations() is not supported with xlrd")

    def max_iterations(self, val=None):
        raise ValueError("ExcelSpreadsheet max_iterations() is not supported with xlrd")

    def calculate(self):
        """
        Perform calculations in a spreadsheet
        """
        raise ValueError("ExcelSpreadsheet calculate() is not supported with xlrd")

    def set_array(self, row, col, val, wsid=None):
        self.activate(wsid)
        nrows=len(val)
        return self.set_range( (self.ws().Cells(row,col), self.ws().Cells(row+nrows-1,col+1)), val)

    def get_array(self, row, col, row2, col2, wsid=None, raw=False):
        return self.get_range( (self.ws().Cells(row,col), self.ws().Cells(row2,col2)), wsid, raw)

    def set_range(self, rangename, val, wsid=None):
        """
        Set a range with a given value (or set of values)
        """
        self.activate(wsid)
        if type(val) in (int,float):
            val=((val,),)
        if len(val) != self.get_range_nrows(rangename):
            raise IOError("Setting data with "+str(len(val))+" rows but range has "+str(self.get_range_nrows(rangename)))
        if type(val) is tuple:
            data = val
        elif type(val) not in (float,int,bool):
            data=[]
            for item in val:
                if type(item) is tuple:
                    data.append(item)
                elif type(item) in (float,int,bool):
                    data.append( (item,) )
                else:
                    data.append(tuple(item))
            data = tuple(data)
        self._range(rangename).Value = data

    def get_column(self, colname, wsid=None, raw=False, contiguous=False):
        """
        Select the values of a column.
        This ignores blank cells at the top and bottom of the column.

        If contiguous is False, a list is returned with all cell values
        starting from the first non-blank cell until the last non-blank cell.

        If contiguous if True, a list is returned with all cell values
        starting from the first non-blank cell until the first blank cell.
        """
        self.activate(wsid)
        name = colname+"1"
        if self.get_range(name) is None:
            start = self.ws().Range(name).End(self.xlDown)
        else:
            start = self.ws().Range(name)
        if contiguous:
            range = self.ws().Range(start, start.End(self.xlDown))
        else:
            range = self.ws().Range(start, self.ws().Range(colname+"65536").End(self.xlUp))
        tmp = self._get_range_data(range, raw)
        return tmp

    def get_range(self, rangename, wsid=None, raw=False):
        """
        Get values for a specified range
        """
        self.activate(wsid)
        rangeid = self._range(rangename)
        return self._get_range_data(rangeid, raw)

    def _get_range_data(self, range, raw):
        if raw:
            return range.Value
        nrows = range.Rows.Count
        ncols = range.Columns.Count
        if range.Columns.Count == 1:
            if nrows == 1:
                #
                # The range is a singleton, so return a float
                #
                return range.Value
            else:
                #
                # The range is a column of data, so return a tuple of floats
                #
                ans=[]
                for val in range.Value:
                    ans.append(val[0])
                return tuple(ans)
        else:
            if nrows == 1:
                #
                # The range is a row of data, so return a tuple of floats
                #
                return range.Value[0]
            else:
                #
                # The range is a two-dimensional array, so return the values
                # as a tuple of tuples.
                #
                #return self._range(rangename).Value
                return range.Value

    def get_range_nrows(self, rangename, wsid=None):
        """
        Get the number of rows in a specified range
        """
        self.activate(wsid)
        return self._range(rangename).Rows.Count

    def get_range_ncolumns(self, rangename, wsid=None):
        """
        Get the number of columns in a specified range
        """
        self.activate(wsid)
        return self._range(rangename).Columns.Count

    def _range(self, rangeid, wsid=None):
        """
        Return a range for a given worksheet
        """
        self.activate(wsid)
        #
        # If rangeid is a tuple, then this is a list of arguments to pass
        # to the Range() method.
        #
        if type(rangeid) is tuple:
            return self.ws().Range(*rangeid)
        #
        # Otherwise, we assume that this is a range name.
        #
        else:
            tmp_= self.wb.name_map.get(rangeid.lower(), None)
            if tmp_ is None:
                raise IOError("Unknown range name `"+str(rangeid)+"'")
            if len(tmp_) > 1:
                raise IOError("Cannot process scoped names")
            return tmp_[0]


