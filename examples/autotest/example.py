#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________
#

import pyutilib.autotest
from pyutilib.component.core import alias
import pyutilib.subprocess


class ExampleTestDriver(pyutilib.autotest.TestDriverBase):
    """
    This test driver executes a unix command and compares its output
    with a baseline value.
    """

    alias('example')

    def run_test(self, testcase, name, options):
        """Execute a single test in the suite"""
        name = options.suite+'_'+name
        cmd = options.solver+' '
        if not options.cat_options is None:
            cmd += options.cat_options+' '
        cmd += options.file
        print( "Running test suite '%s'  test '%s'  command '%s'" % \
                (options.suite, name, cmd))
        pyutilib.subprocess.run(cmd, outfile=options.currdir+'test_'+name+".out")
        testcase.failUnlessFileEqualsBaseline(
                options.currdir+'test_'+name+".out",
                options.currdir+'test_'+name+".txt")
