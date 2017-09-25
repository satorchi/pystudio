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
    s.connect(("134.158.186.162", 33576))
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
    return oxford_send_cmd('SET:SYS:USER:NORM\n')

def oxford_set_point(self, T=None):
    '''
    set the loop set point for bath temperature
    '''
    if (not isinstance(T,float)) and (not isinstance(T,int)):
        print('ERROR! invalid temperature')
        return None

    # first initialize Oxford Inst.
    d=oxford_init()

    # now send the loop set command
    cmd='SET:DEV:T5:TEMP:LOOP:TSET:%0.2f\n' % T
    return send_oxford_cmd(cmd)


def oxford_read_bath_temperature(self):
    '''
    read the current bath temperature of the dilution fridge
    '''
    cmd='READ:DEV:T5:TEMP:SIG:TEMP\n'
        
    d=send_oxford_cmd(cmd)
    try:
        T=eval(d[-1].replace('K',''))
    except:
        T=d[-1]
    return T

