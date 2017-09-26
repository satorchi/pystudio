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
'''
from __future__ import division, print_function
import numpy as np
import pickle
import socket
    
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

def oxford_set_point(self, T=None):
    '''
    set the loop set point for bath temperature, and activate the loop
    '''
    if (not isinstance(T,float)) and (not isinstance(T,int)):
        print('ERROR! invalid temperature')
        return None

    # first initialize Oxford Inst.
    d=self.oxford_init()

    # now send the loop set and activate command
    cmd='SET:DEV:T5:TEMP:LOOP:TSET:%0.2f\nSET:DEV:T5:TEMP:LOOP:MODE:ON\n' % T
    return self.oxford_send_cmd(cmd)

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

