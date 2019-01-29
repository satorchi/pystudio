#!/usr/bin/env python
'''
$Id: run_calibration_source.py
$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
$created: Tue 29 Jan 2019 14:19:05 CET
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

run a measurement with the calibration source
  - switch on calibration source, modulator, amplifier, and arduino
  - configure modulator, calibration source
  - acquire data using the arduino
'''
from __future__ import division, print_function
import os,sys

def helptxt():
    '''
    some help text
    '''
    print('usage: %s duration=<duration in seconds>')
    return


# parse arguments
# read the duration if given
duration_seconds = None
for arg in sys.argv:
    arg = arg.upper()
    if arg.find('DURATION=')==0:
        vals = arg.split('=')
        try:
            duration_seconds = eval(vals[1])
        except:
            print('unable to read duration.')
        continue

    # maybe the duration was given on its own without the prefix "duration="
    if duration_seconds is None:
        try:
            duration_seconds = eval(arg)
        except:
            pass
        
        
if duration_seconds is None:
    helptxt()
    quit()


# avoid X11 errors.  No plotting to screen.
import matplotlib
matplotlib.use('Agg')

# qubicpack tools for commanding various hardware
from qubicpack.modulator import modulator
from qubicpack.arduino import arduino
from qubicpack.calibration_source import calibration_source

# this is for the Energenie smart powerbar to switch on/off the devices
from PyMS import PMSDevice
energenie = PMSDevice('energenie', '1')

energenie_socket = {}
energenie_socket['modulator'] = 0
energenie_socket['calibration source'] = 1
energenie_socket['lamp'] = 2
energenie_sockert['amplifier'] = 3

# switch on devices
for dev in ['modulator','calibration source','amplifier']:
    energenie.set_socket_states({energenie_socket[dev]:True})

# initialize devices
mod = modulator()
mod.configure(frequency=0.33,duty=33)

calsrc = calibration_source('LF')
calsrc.set_Frequency(150)

ard = arduino()
ard.init()

# make an acquisition
startTime = dt.datetime.utcnow()
t,v = ard.acquire(duration=duration_seconds)

# write the result to file
outfile = startTime.strftime('calsource_%Y%m%dT%H%M%S.dat')
h=open(outfile,'w')
for idx,val in enumerate(v):
    tstamp = t[idx].strftime('%s.%f')
    h.write('%s %i' % (tstamp,val))
h.close()
print('output file written: %s' % outfile)


