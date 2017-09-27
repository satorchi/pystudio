#!/usr/bin/env python
'''
$Id: oxford.py
$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
$created: Mon 25 Sep 2017 16:26:59 CEST
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

control and read output from the Oxford Instruments Triton dilution fridge

see document: "Triton manual issue 3.7.pdf" (page 100)
I put it on the QUBIC wiki.  Here's the link:
http://qubic.in2p3.fr/wiki/uploads/DetectorWorkingGroup/MeasurementsDetectors/Triton%20manual%20issue%203.7.pdf
'''
from __future__ import division, print_function
import numpy as np
import socket,time

def oxford_send_cmd(self, cmd=None):
    '''
    send a command to the Oxford Instruments control computer for the dilution fridge
    '''
    if cmd==None:
        cmd='READ:SYS:TIME\n'

    if not isinstance(cmd,str):
        print('please enter a valid command')
        return None

    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(("134.158.186.162", 33576))
    except:
        print('ERROR! network not available.')
        return None
    s.send(cmd)

    d=''
    b=''
    count=0
    while not b=='\n':
        b=s.recv(1)
        d+=b
        count+=1

    #print('return length: %i' % count)
    s.close()
    return d.strip('\n').split(':')


def oxford_init(self):
    '''
    initialize the Oxford Instruments computer so it accepts commands
    '''
    return self.oxford_send_cmd('SET:SYS:USER:NORM\n')

def oxford_pidoff(self):
    '''
    switch off the temperature control loop
    '''
    pidoff='SET:DEV:T5:TEMP:LOOP:MODE:OFF\n'
    d=self.oxford_init()
    return self.oxford_send_cmd(pidoff)

def oxford_set_point(self, T=None, heater=0.1, ramp=0.1):
    '''
    configure the loop set point for bath temperature, and activate the loop
    '''
    if (not isinstance(T,float)) and (not isinstance(T,int)):
        print('ERROR! invalid temperature')
        return None

    # first initialize Oxford Inst.
    d=self.oxford_init()

    # activate the loop:  This must be done first!
    # and then configure the temperature set-point
    cmd ='SET:DEV:T5:TEMP:LOOP:MODE:ON\n'        # ON/OFF
    cmd+='SET:DEV:T5:TEMP:LOOP:TSET:%0.2f\n' % T # K
    d=self.oxford_send_cmd(cmd)

    # wait a second and then activate the heater
    time.sleep(1)
    cmdheat='SET:DEV:T5:TEMP:LOOP:RANGE:%f\n' % heater # mA
    d=self.oxford_send_cmd(cmdheat)

    # set the ramp rate for temperature control
    cmdramp='SET:DEV:T5:TEMP:LOOP:RAMP:RATE:%f\n' % ramp # K/min
    d=self.oxford_send_cmd(cmdramp)

    # enable the ramp
    time.sleep(1)
    rampenable='SET:DEV:T5:TEMP:LOOP:RAMP:ENAB:ON\n'
    d=self.oxford_send_cmd(cmdramp)
    
    return d

def oxford_read_set_point(self):
    '''
    read the loop set point for bath temperature
    '''
    cmd='READ:DEV:T5:TEMP:LOOP:TSET\n'
    d=self.oxford_send_cmd(cmd)
    try:
        T=eval(d[-1].replace('K',''))
    except:
        print('ERROR! could not read set point temperature: %s' % d)
        return None
    return T

def oxford_read_temperature(self,chan=5):
    '''
    read the temperature from one of the thermometers
    '''
    if not isinstance(chan,int):
        print('ERROR! invalid thermometer channel.  Enter a number from 1 to 10.')
        return None
    
    cmd='READ:DEV:T%i:TEMP:SIG:TEMP\n' % chan
    d=self.oxford_send_cmd(cmd)
    try:
        T=eval(d[-1].replace('K',''))
    except:
        print('ERROR! could not read temperature: %s' % d)
        return None
    return T
    

def oxford_read_bath_temperature(self):
    '''
    read the bath temperature of the dilution fridge
    '''
    cmd='READ:DEV:T5:TEMP:SIG:TEMP\n'
        
    d=self.oxford_send_cmd(cmd)
    try:
        T=eval(d[-1].replace('K',''))
    except:
        print('ERROR! could not read bath temperature: %s' % d)
        return None

    return self.assign_temperature(T)

