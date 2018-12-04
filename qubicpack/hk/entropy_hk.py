#!/usr/bin/env python
'''
$Id: entropy_hk.py
$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
$created: Mon 03 Dec 2018 07:42:50 CET
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

class to read data from Entropy controlled devices
AVS47 temperatures
Mechanical heat switches
'''
from __future__ import division, print_function
import socket
import re

from satorchipy.datefunctions import *

class entropy_hk :
    def __init__(self,hostname=None):
        '''initialize an instance of entropy_hk
        '''

        self.MAX_MSGLEN=4096
        self.MECH_CLOSED=160000 # position of switch closed
        self.MECH_OPEN=0 # position of switch full open
        self.mech_idx=None
        self.verbosity=0
        
        if hostname is None:
            self.hostname='apcbrain2.in2p3.fr'
        else:
            self.hostname=hostname

        self.init_socket()
        self.get_device_list()
        self.get_startTime()
        return None

    def debugmsg(self,msg):
        '''print a message to screen for debugging
        '''
        if self.verbosity>0:print(msg)
        return None

    def init_socket(self):
        '''initialize the connection to the Entropy machine
        '''
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.hostname,2002))
        self.socket=s
        self.socket.settimeout(2)
        a=self.socket.recv(self.MAX_MSGLEN)
        self.debugmsg(a)
        return None

    def get_startTime(self):
        '''get the start time for logging temperatures
        all temperature times are given as an offset from this time
        '''
        self.socket.send('dateTime AppStart\n')
        a=self.socket.recv(self.MAX_MSGLEN)
        self.startTime=str2dt(a)
        print('Logging start time: %s' % self.startTime.strftime('%Y-%m-%d %H:%M:%S.%f'))
        return self.startTime
    
    def get_device_list(self):
        '''get the valid device names
        '''
        self.socket.send('deviceList\n')
        devlist_txt=self.socket.recv(self.MAX_MSGLEN)
        lines=devlist_txt.split('\n')
        devlist=[]
        idx=0
        self.mech_idx=None
        for line in lines:
            if line[0:3]==' - ':
                dev=line[3:].strip()
                devlist.append(dev)
                match=re.match('.*[Mm]ech.*',dev)
                if match:
                    self.mech_idx=idx
                idx+=1
        self.devlist=devlist
        self.print_device_list()
        return devlist


    def print_device_list(self):
        '''print out a list of valid devices
        '''
        print('devices:')
        for idx,dev in enumerate(self.devlist):
            print('   %i) %s' % (idx,dev))

        return None
    
    def get_temperature(self,ch=None,dev=None):
        '''get a temperature reading
        '''
        if dev is None:
            print('Please enter a valid device!')
            return self.print_device_list()

        if ch is None:ch=0
        cmd='device %s temperature? %i\n' % (dev,ch)
        self.socket.send(cmd)
        a=self.socket.recv(self.MAX_MSGLEN)
        cols=a.strip().replace(',','').split()
        try:
            T=float(cols[0])
        except:
            self.debugmsg("Couldn't read temperature: %s" % cols[0])
            T=None

        try:
            tstamp=int(cols[1])
        except:
            self.debugmsg("Couldn't read timestamp: %s" % cols[1])
            tstamp=-1

        return (tstamp,T)


    def mech_get_position(self,ch=None):
        '''get the current position of one of the heat switches
        '''

        if self.mech_idx is None:
            print('ERROR! Could not find the mechanical heat switch device')
            return None
        
        if ch is None:
            print('Please enter which heat switch, 1 or 2')
            return None

        cmd='device %s absolute? %i\n' % (self.devlist[self.mech_idx],ch)
        self.socket.send(cmd)
        a=self.socket.recv(self.MAX_MSGLEN)
        self.debugmsg(a)
        cols=a.strip().replace(',','').split()
        
        try:
            pos=int(cols[0])
        except:
            pos=None

        try:
            tstamp=int(cols[1])
        except:
            tstamp=-1

        return (tstamp,pos)
        
    def mech_command(self,ch=None,steps=None,command=None):
        '''open/close/stop a mechanical heat switch by some steps
        '''

        if self.mech_idx is None:
            print('ERROR! Could not find the mechanical heat switch device')
            return None
        
        if ch is None:
            print('Please enter which heat switch, 1 or 2')
            return None

        if command is None:command='stop'
        command=command.lower()
        if command not in ['open','close','stop']:
            print('ERROR! Please enter a valid command (open/close/stop)')
            return None

        if command in ['open','close']:
            if steps is None:
                print('Please enter a number of steps')
                return None
            cmd='device %s %s %i %i\n' % (self.devlist[self.mech_idx],command,ch,steps)
        else:
            cmd='device %s %i stop\n' % (self.devlist[self.mech_idx],ch)
        
        self.socket.send(cmd)
        return True

    def mech_open(self,ch=None,steps=None):
        '''wrapper for easy access to the open command
        '''
        if steps is None:
            # find the number of steps necessary to open completely
            pos=self.mech_get_position(ch)
            steps=pos-self.MECH_OPEN            
        return self.mech_command(ch,steps,command='open')

    def mech_close(self,ch=None,steps=None):
        '''wrapper for easy access to the close command
        '''
        if steps is None:
            # find the number of steps necessary to close completely
            pos=self.mech_get_position(ch)
            steps=self.MECH_CLOSED - pos
        return self.mech_command(ch,steps,command='close')

    def mech_stop(self,ch=None):
        '''wrapper for easy access to the stop command
        '''
        return self.mech_command(ch,command='stop')

    def get_logtime(self,timestamp):
        '''get the actual log time from the offset time
        offset time is given in milliseconds
        '''
        logtime_unix=float(self.startTime.strftime('%s.%f')) + 1e-3*timestamp
        logtime=dt.datetime.fromtimestamp(logtime_unix)
        return logtime
    
        
    
