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
import time,socket,re

from satorchipy.datefunctions import *

class entropy_hk :
    def __init__(self,hostname=None):
        '''initialize an instance of entropy_hk
        '''

        self.MAX_MSGLEN=4096
        self.MECH_CLOSED=190000 # position of switch closed
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
        self.assign_labels()
        return None

    def log(self,msg):
        '''messages to log file and to screen
        '''
        now=dt.datetime.now()
        logmsg='%s | %s' % (now.strftime('%Y-%m-%d %H:%M:%S'),msg)
        h=open('hk_entropy.log','a')
        h.write(logmsg+'\n')
        h.close()
        print(logmsg)
        return

    def assign_labels(self):
        '''label for each channel
        copied Tue 04 Dec 2018 10:36:26 CET
        '''
        label={}
        label['AVS47_1']=[]
        label['AVS47_2']=[]
        
        label['AVS47_1'].append('Touch')
        label['AVS47_1'].append('1K stage')
        label['AVS47_1'].append('RIRT 300mK stage')
        label['AVS47_1'].append('M1')
        label['AVS47_1'].append('Cold head 1K')
        label['AVS47_1'].append('Film breaker')
        label['AVS47_1'].append('Cold head 300mK')
        label['AVS47_1'].append('M2')
        label['AVS47_2'].append('1K link')
        label['AVS47_2'].append('PT2 cold head')
        label['AVS47_2'].append('Fridge assembly right')
        label['AVS47_2'].append('Mech HS support')
        label['AVS47_2'].append('Fridge assembly left')
        label['AVS47_2'].append('UNUSED')
        label['AVS47_2'].append('UNUSED')
        label['AVS47_2'].append('UNUSED')
        self.label=label
        return label
    
    def debugmsg(self,msg):
        '''print a message to screen for debugging
        '''
        if self.verbosity>0:self.log(msg)
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

    def sendreceive(self,cmd):
        '''send a command and receive the answer
        '''
        self.socket.send(cmd)
        try:
            a=self.socket.recv(self.MAX_MSGLEN)
        except:
            self.log("ERROR!  Communication error.  Trying to re-initialize socket.")
            self.socket.close()
            self.init_socket()
            a=None
        return a

    def get_startTime(self):
        '''get the start time for logging temperatures
        all temperature times are given as an offset from this time
        '''
        a=self.sendreceive('dateTime AppStart\n')
        if a is None:return None
        
        self.startTime=str2dt(a)
        self.log('Logging start time: %s' % self.startTime.strftime('%Y-%m-%d %H:%M:%S.%f'))
        return self.startTime
    
    def get_device_list(self):
        '''get the valid device names
        '''
        devlist_txt=self.sendreceive('deviceList\n')
        if devlist_txt is None:return None
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
        self.log(devlist)
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
            self.log('Please enter a valid device!')
            return self.print_device_list()

        if ch is None:ch=0
        cmd='device %s temperature? %i\n' % (dev,ch)
        a=self.sendreceive(cmd)
        if a is None:return None,None

        cols=a.strip().replace(',','').split()
        try:
            T=float(cols[0])
        except:
            self.debugmsg("Couldn't read temperature: %s" % cols)
            T=None

        try:
            tstamp_entropy=int(cols[1])
            msec=self.startTime.strftime('%f')[0:3]
            tstamp=int('%s%s' % (self.startTime.strftime('%s'),msec))            
        except:
            self.debugmsg("Couldn't read timestamp: %s" % cols)
            tstamp=-1

        return (tstamp,T)


    def mech_get_position(self,ch=None):
        '''get the current position of one of the heat switches
        Note: no timestamp is returned!
        '''

        if self.mech_idx is None:
            self.log('ERROR! Could not find the mechanical heat switch device')
            return None
        
        if ch is None:
            self.log('Please enter which heat switch, 1 or 2')
            return None

        cmd='device %s absolute? %i\n' % (self.devlist[self.mech_idx],ch)
        a=self.sendreceive(cmd)
        if a is None:return None

        self.debugmsg(a)
        cols=a.strip().replace(',','').split()
        
        try:
            pos=int(cols[0])
        except:
            self.debugmsg("Couldn't read position: %s" % cols)
            pos=None

        return pos
        
    def mech_command(self,ch=None,steps=None,command=None):
        '''open/close/stop a mechanical heat switch by some steps
        '''

        if self.mech_idx is None:
            self.log('ERROR! Could not find the mechanical heat switch device')
            return None
        
        if ch is None:
            self.log('Please enter which heat switch, 1 or 2')
            return None

        if command is None:command='stop'
        command=command.lower()
        if command not in ['open','close','stop']:
            self.log('ERROR! Please enter a valid command (open/close/stop)')
            return None

        if command in ['open','close']:
            if steps is None:
                self.log('Please enter a number of steps')
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
    
        
    def wait_for_position(self,ch,position,timeout=300):
        '''wait for the mechanism to reach its position
        '''
        tolerance=1000
        now=dt.datetime.now()
        endtime=now+dt.timedelta(seconds=timeout)
        delta=100000

        while delta>tolerance and now<endtime:
            current_position=self.mech_get_position(ch)
            delta=abs(current_position - position)
            if delta>tolerance:
                time.sleep(1)
            now=dt.datetime.now()

        return
    
    def close(self):
        ''' close the socket
        '''
        self.socket.close()
        return
    
