#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

from setuptools import setup

setup(
    name='Package5',
    version='0.1',
    packages=['package5'],
    package_data={'package5': []},
    author='Jane Doe',
    author_email='jdoe@dev.null',
    description='Package5 description.',
    license='BSD',
    keywords='package5 plugin',
    classifiers=[
        'Framework :: Package5',
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    install_requires=['PyUtilib==100.0'],
    entry_points={
        'project1.plugins': [
            'package5.main = package5.main',
        ]
    })
