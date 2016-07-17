#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

from setuptools import setup

setup(
    name='Package2',
    version='0.1',
    packages=['package2'],
    package_data={'package2': []},
    author='Jane Doe',
    author_email='jdoe@dev.null',
    description='Package2 description.',
    license='BSD',
    keywords='package2 plugin',
    classifiers=[
        'Framework :: Package2',
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],

    #install_requires = ['Trac>=0.11', 'Genshi>=0.5'],
    entry_points={
        'project2.plugins': [
            'package2.main = package2.main',
        ]
    })
