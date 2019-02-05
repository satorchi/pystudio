#!/usr/bin/env python
'''
$Id: calsource_set_frequency.py
$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
$created: Tue 05 Feb 2019 11:24:47 CET
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

simple script to set the frequency of the calibration source
'''
from __future__ import division, print_function
import sys

# import matplotlib even though we don't need it, and ensure that we don't make calls to Xserver
import matplotlib
matplotlib.use('Agg')

# import the calibration_source class
from qubicpack.calibration_source import calibration_source


# parse command line arguments
if len(sys.argv)<=1:
    freq = 150.0
    print('usage: %s <frequency>  - default frequency is %.0fGHz' % (sys.argv[0],freq))

val = None
for arg in sys.argv:
    try:
        val = eval(arg)
    except:
        pass

if val is not None:
    freq = val


print('initializing calibration source')
calsrc = calibration_source('LF')
if calsrc is not None:
    calsrc.set_Frequency(freq)
