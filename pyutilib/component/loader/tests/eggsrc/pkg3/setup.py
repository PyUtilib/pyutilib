#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

from setuptools import setup

setup(
    name='Package3',
    version='0.1',
    packages=['package3'],
    package_data={'package3': []},
    author='Jane Doe',
    author_email='jdoe@dev.null',
    description='Package3 description.',
    license='BSD',
    keywords='package3 plugin',
    classifiers=[
        'Framework :: Package3',
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
            'package3.main = package3.main',
        ]
    })
