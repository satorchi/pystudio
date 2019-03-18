#! /usr/bin/env python
'''
$Id: setup_qubicpack.py
$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
$created: Mon 07 Aug 2017 08:35:24 CEST
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

setup.py for qubicpack only.  
Use this to install qubicpack without pystudio
'''
from __future__ import division, print_function
import os,sys,subprocess
from numpy.distutils.core import setup

DISTNAME         = 'qubicpack'
DESCRIPTION      = 'Utilities for QUBIC detector data visualization'
AUTHOR           = 'Steve Torchinsky'
AUTHOR_EMAIL     = 'satorchi@apc.in2p3.fr'
MAINTAINER       = 'Steve Torchinsky'
MAINTAINER_EMAIL = 'satorchi@apc.in2p3.fr'
URL              = 'https://github.com/satorchi/pystudio'
LICENSE          = 'GPL'
DOWNLOAD_URL     = 'https://github.com/satorchi/pystudio'
VERSION          = '2.0.0'

with open('README.md') as f:
    long_description = f.readlines()

msg  = "QUBICPACK is now in a separate repository!\n"
msg += "Please create a new local respository with:\n"
msg += "$ git clone https://github.com/satorchi/qubicpack.git\n\n"
print(msg)

