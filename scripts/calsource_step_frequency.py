#!/usr/bin/env python
'''
$Id: calsource_step_frequency.py
$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
$created: Sun  3 Feb 23:21:13 CET 2019
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

step through frequencies on the calibration source
'''
from __future__ import division, print_function          
import time
import datetime as dt

from qubicpack.calibration_source import calibration_source
print('initializing calibration source')
calsrc = calibration_source('LF')

# step through frequencies
integration_time = 60.0

freq_min = 130.0
freq_max = 170.0

freq = freq_min
delta_freq = 2.5
while freq <= freq_max:
    calsrc.set_Frequency(freq)
    h = open('calsource_step_frequency.log','a')
    tstamp = dt.datetime.utcnow().strftime('%s.%f')
    h.write('%s %f\n' % (tstamp,freq))
    h.close()
    time.sleep(integration_time)
    freq += delta_freq

    
