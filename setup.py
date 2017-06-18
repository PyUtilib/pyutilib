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

import sys
import os
from setuptools import setup


def _find_packages(path):
    """
    Generate a list of nested packages
    """
    pkg_list=[]
    if not os.path.exists(path):
        return []
    if not os.path.exists(path+os.sep+"__init__.py"):
        return []
    else:
        pkg_list.append(path)
    for root, dirs, files in os.walk(path, topdown=True):
        if root in pkg_list and "__init__.py" in files:
            for name in dirs:
                if os.path.exists(root+os.sep+name+os.sep+"__init__.py"):
                    pkg_list.append(root+os.sep+name)
    return [pkg for pkg in map(lambda x:x.replace(os.sep,"."), pkg_list)]

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

packages = _find_packages('pyutilib')

requires=[ 'nose', 'six' ]
if sys.version_info < (2,7):
    requires.append('argparse')
    requires.append('ordereddict')
    requires.append('unittest2')

setup(name="PyUtilib",
    version='5.5.1',
    maintainer='William E. Hart',
    maintainer_email='wehart@sandia.gov',
    url = 'https://github.com/PyUtilib/pyutilib',
    license = 'BSD',
    platforms = ["any"],
    description = 'PyUtilib: A collection of Python utilities',
    long_description = read('README.txt'),
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
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: Jython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'],
      packages=packages,
      keywords=['utility'],
      namespace_packages=['pyutilib', 'pyutilib.component'],
      install_requires=requires,
      entry_points="""
        [pyutilib.component]
        component.app = pyutilib.component.app
        component.config = pyutilib.component.config
        component.executables = pyutilib.component.executables
        component.loader = pyutilib.component.loader
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

