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
now=dt.datetime.utcnow()
stoptime=now+dt.timedelta(days=7)

# we watch the Mechanical Heat Switch support
dev='AVS47_2'
ch=3

# current temperature
tstamp,T=hk.get_temperature(dev=dev,ch=ch)

# We'll start with an immediate open/close
Tnext=T+0.1
while now < stoptime and T>40.0:

    now=dt.datetime.utcnow()
    tstamp,T=hk.get_temperature(dev=dev,ch=ch)
    if T is not None:
        print('%s | Current temperature: %.1fK.  Next target temperature: %.1fK' % (now.strftime('%Y-%m-%d %H:%M:%S.%f UT'),T,Tnext))
    if T is not None and T<Tnext:
        now=dt.datetime.utcnow()
        print('%s | Opening Mechanical Heat Switches' % now.strftime('%Y-%m-%d %H:%M:%S.%f UT'))
        hk.mech_open(1)
        hk.wait_for_position(1,hk.MECH_OPEN)
        hk.mech_open(2)
        hk.wait_for_position(1,hk.MECH_OPEN)
        
        now=dt.datetime.utcnow()            
        print('%s | Closing Mechanical Heat Switches' % now.strftime('%Y-%m-%d %H:%M:%S.%f UT'))
        hk.mech_close(1)
        hk.wait_for_position(1,hk.MECH_CLOSED)
        hk.mech_close(2)
        hk.wait_for_position(1,hk.MECH_CLOSED)

        Tnext=T-20

    time.sleep(1)
    
