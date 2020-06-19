#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

"""
Setup for PyUtilib package
"""

import os
from setuptools import setup, find_packages

def read(*rnames):
    with open(os.path.join(os.path.dirname(__file__), *rnames)) as README:
        # Strip all leading badges up to, but not including the COIN-OR
        # badge so that they do not appear in the PyPI description
        while True:
            line = README.readline()
            if 'COIN-OR' in line:
                break
            if line.strip() and '[![' not in line:
                break
        return line + README.read()

requires=[ 'nose', 'six' ]

setup(name="PyUtilib",
    version='6.0.1.dev0',
    maintainer='William E. Hart',
    maintainer_email='wehart@sandia.gov',
    url = 'https://github.com/PyUtilib/pyutilib',
    license = 'BSD',
    platforms = ["any"],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
    description = 'PyUtilib: A collection of Python utilities',
    long_description = read('README.md'),
    long_description_content_type='text/markdown',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: Jython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'],
      packages=find_packages(),
      keywords=['utility'],
      install_requires=requires,
      entry_points="""
        [nose.plugins.0.10]
        nose.testdata = pyutilib.th.nose_testdata:TestData
        nose.forcedgc = pyutilib.th.nose_gc:ForcedGC
        nose.timeout = pyutilib.th.nose_timeout:TestTimeout
        [console_scripts]
        test.pyutilib = pyutilib.dev.runtests:runPyUtilibTests
        lbin = pyutilib.dev.lbin:main
        lpython = pyutilib.dev.lpython:main
        pypi_downloads = pyutilib.dev.pypi_downloads:main
        replaceCopyright = pyutilib.dev.replaceCopyright:main
        checkCopyright = pyutilib.dev.checkCopyright:main
        pyutilib_test_driver = pyutilib.autotest.driver:main
        dispatch_srvr=pyutilib.pyro.dispatch_srvr:main
      """
      )

