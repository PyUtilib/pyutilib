#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

from setuptools import setup

setup(
    name='Package4',
    version='0.1',
    packages=['package4'],
    package_data={'package4': []},
    author='Jane Doe',
    author_email='jdoe@dev.null',
    description='Package4 description.',
    license='BSD',
    keywords='package4 plugin',
    classifiers=[
        'Framework :: Package4',
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    install_requires=['PyUtilibDummyProject>=0.11'],
    entry_points={
        'project1.plugins': [
            'package4.main = package4.main',
        ]
    })
