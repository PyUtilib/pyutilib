#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

from setuptools import setup

setup(
    name='Package1',
    version='0.1',
    packages=['package1'],
    package_data={'package1': []},
    author='Jane Doe',
    author_email='jdoe@dev.null',
    description='Package1 description.',
    license='BSD',
    keywords='package1 plugin',
    classifiers=[
        'Framework :: Package1',
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],

    #install_requires = ['Trac>=0.11', 'Genshi>=0.5'],
    entry_points={
        'project1.plugins': [
            'package1.main = package1.main',
        ]
    })
