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

readme_file = os.path.join(os.path.dirname(__file__), 'README')

setup(name='ircutils',
      version='0.1.3',
      description='IRC framework and utilities. Great for bot creation.',
      long_description=open(readme_file).read(),
      author='Evan Fosmark',
      author_email='evan.fosmark@gmail.com',
      url='http://dev.guardedcode.com/projects/ircutils/',
      license="MIT/X11",
      platforms="Any",
      packages=['ircutils'],
      classifiers=[
         "Development Status :: 3 - Alpha",
         "Intended Audience :: Developers",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
         "Programming Language :: Python",
         "Topic :: Communications :: Chat :: Internet Relay Chat",
         "Topic :: Software Development :: Libraries :: Application Frameworks",
         "Topic :: Software Development :: Libraries :: Python Modules"
         ]
     )