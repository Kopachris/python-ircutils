#!/usr/bin/env python3
## ----------------------------------------------------------------------------#
## IRCUtils setup file.
## To install, type the following in console in this directory:
##
##     python setup.py install
##
## To ensure that installation was a success, you may want to open up a Python
## console and try to import the package.
## ----------------------------------------------------------------------------#
from setuptools import setup
import os

readme_file = os.path.join(os.path.dirname(__file__), 'README')

setup(name='ircutils',
    version='0.3.1',
    description='IRC framework and utilities. Great for bot creation.',
    long_description=open(readme_file).read(),
    author=['Christopher Koch', 'Evan Fosmark'],
    author_email=['ch_koch@outlook.com', 'evan.fosmark@gmail.com'],
    url='http://dev.guardedcode.com/projects/ircutils/',
    license="BSD 3-Clause",
    platforms="Any",
    packages=['ircutils'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Communications :: Chat :: Internet Relay Chat",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules"
        ]
    )