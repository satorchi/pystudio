#!/usr/bin/env python
'''
$Id: calsource_commander.py
$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
$created: Fri 08 Feb 2019 15:52:18 CET
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

This is the Calibration Source commander.

It has two components:  
   "commander" is the command line interface
   "manager" is run on the Raspberry Pi which interfaces with the hardware

by default, this script will run as the "commander"
invoke with command line argument "manager" to run the "manager"
'''
from __future__ import division, print_function
import sys

# avoid error message because of Xorg server inaccessible
import matplotlib
matplotlib.use('Agg')

from qubicpack.calsource_configuration_manager import calsource_configuration_manager

role = 'commander'
for arg in sys.argv:
    if arg.lower() == 'manager':
        role = 'manager'
        continue

    if arg.lower() == 'commander':
        role = 'commander'
        continue

cli = calsource_configuration_manager(role=role)


    
