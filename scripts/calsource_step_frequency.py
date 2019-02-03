#!/usr/bin/env python

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

    
