#!/usr/bin/env python
'''
$Id: mech_openclose.py
$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
$created: Tue 04 Dec 2018 22:35:58 CET
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

open/close the Mechanical heat switches at 20K intervals
'''
from __future__ import division, print_function
import sys,os,subprocess,time,socket
import numpy as np
import datetime as dt

from qubicpack.hk.entropy_hk import entropy_hk


hk=entropy_hk()

# hostname
cmd='/sbin/ifconfig eth0'
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
out,err=proc.communicate()
for line in out.split('\n'):
    if line.find('inet ')>0: break
hostname=line.split()[1]
print('hostname=%s' % hostname)


# don't go forever
now=dt.datetime.now()
stoptime=now+dt.timedelta(days=7)

# we watch the Mechanical Heat Switch support
dev='AVS47_2'
ch=3

# current temperature
tstamp,T=hk.get_temperature(dev=dev,ch=ch)

# We'll start with an immediate open/close
Tnext=T+0.1

while now < stoptime and T>40.0:

    now=dt.datetime.now()
    tstamp,T=hk.get_temperature(dev=dev,ch=ch)
    if T<Tnext:
        print('Opening/Closing Mechanical Heat Switches')
        print('%s %.3fK' % (now.strftime('%Y-%m-%d %H:%M:%S.%f'),T))
        hk.mech_open(1)
        hk.wait_for_position(1,hk.MECH_OPEN)
        hk.mech_open(2)
        hk.wait_for_position(1,hk.MECH_OPEN)
        

        hk.mech_close(1)
        hk.wait_for_position(1,hk.MECH_CLOSED)
        hk.mech_close(2)
        hk.wait_for_position(1,hk.MECH_CLOSED)

        Tnext=T-20
        print('Next target temperature: %.1fK' % Tnext)

    time.sleep(1)
    
