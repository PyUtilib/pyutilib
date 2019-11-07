#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

from setuptools import setup

setup(
    name='Package7',
    version='0.1',
    packages=['package7'],
    package_data={'package7': []},
    author='Jane Doe',
    author_email='jdoe@dev.null',
    description='Package7 description.',
    license='BSD',
    keywords='package7 plugin',
    classifiers=[
        'Framework :: Package7',
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    install_requires=['PyUtilib[FOO]'],
    entry_points={
        'project1.plugins': [
            'package7.main = package7.main',
        ]
    })
