#!/usr/bin/env python
## ----------------------------------------------------------------------------#
## IRCUtils setup file.
## To install, type the following in console in this directory:
##
##     python setup.py install
##
## To ensure that installation was a success, you may want to open up a Python
## console and try to import the package.
## ----------------------------------------------------------------------------#
from distutils.core import setup
import os

# The README.txt file gets used as the description
readme_file = os.path.join(os.path.dirname(__file__), 'README.txt')

setup(name='IRCUtils',
      version='0.1.2',
      description='Pythonic IRC framework and utilities.',
      long_description=open(readme_file).read(),
      author='Evan Fosmark',
      author_email='evan.fosmark@gmail.com',
      url='http://dev.guardedcode.com/projects/ircutils/',
      license="MIT/X11",
      platforms="Any",
      packages=['ircutils'],
      classifiers=[
         "Development Status :: 4 - Beta",
         "Intended Audience :: Developers",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
         "Programming Language :: Python",
         "Topic :: Communications :: Chat :: Internet Relay Chat",
         "Topic :: Software Development :: Libraries :: Application Frameworks",
         "Topic :: Software Development :: Libraries :: Python Modules"
         ]
     )