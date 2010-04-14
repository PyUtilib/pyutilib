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
from setuptools import setup


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(name="PyUtilib",
    version='3.0.1741',
    maintainer='William E. Hart',
    maintainer_email='wehart@sandia.gov',
    url = 'https://software.sandia.gov/trac/pyutilib.ply',
    license = 'BSD',
    platforms = ["any"],
    description = 'PyUtilib: A collection of Python utilities',
    long_description = read('README.txt'),
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Unix Shell',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Software Development :: Libraries :: Python Modules'],
      packages=['pyutilib'],
      keywords=['utility'],
      namespace_packages=['pyutilib'],
      install_requires=[
            'pyutilib.common>=3.0.3',
            'pyutilib.component.app>=3.1.1', 
            'pyutilib.component.config>=3.2.1',
            'pyutilib.component.core>=3.2.1',
            'pyutilib.component.doc>=1.0',
            'pyutilib.component.executables>=3.2.1',
            'pyutilib.component.loader>=3.2.1',
            'pyutilib.dev>=1.6',
            'pyutilib.enum>=1.0.4',
            'pyutilib.excel>=3.0.3',
            'pyutilib.math>=3.0.3',
            'pyutilib.misc>=3.4',
            'pyutilib.ply>=3.0.3',
            'pyutilib.pyro>=3.1.2',
            'pyutilib.R>=3.0.3',
            'pyutilib.services>=3.1.1',
            'pyutilib.subprocess>=3.2',
            'pyutilib.th>=3.1',
            'pyutilib.virtualenv>=1.4.2',
            'nose',
            'unittest2'
      ]
      )

