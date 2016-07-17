#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________


class StreamIndenter(object):
    """Mock-up of a file-like object that wraps another file-like object
    and indents all data using the specified string before passing it to
    the underlying file.  Since this presents a full file interface,
    StreamIndenter objects may be arbitrarily nested."""

    def __init__(self, ostream, indent="        "):
        self.os = ostream
        self.indent = indent
        self.newline = True

    def __getattr__(self, name):
        return getattr(self.os, name)

    def write(self, str):
        if not len(str):
            return
        if self.newline:
            self.os.write(self.indent)
            self.newline = False
        frag = str.rsplit('\n', 1)
        self.os.write(frag[0].replace('\n', '\n' + self.indent))
        if len(frag) > 1:
            self.os.write('\n')
            if len(frag[1]):
                self.os.write(self.indent + frag[1])
            else:
                self.newline = True

    def writelines(self, sequence):
        for x in sequence:
            self.write(x)
