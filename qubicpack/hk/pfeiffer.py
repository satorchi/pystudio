#!/usr/bin/env python
'''
$Id: pfeiffer.py
$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
$created: Tue 08 Jan 2019 19:05:48 CET
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

read the Pfeiffer pressure sensor
'''
from __future__ import division, print_function
import os,sys,serial
import datetime as dt

class Pfeiffer :

    def __init__(self,port=None):
        '''initialize an instance of Pfeiffer
        '''
        self.port=None
        self.info=None
        self.device_ok=False

        if port is None:
            print('NOTE: Please give a device (e.g. port="/dev/ttyUSB0")')
            print('    : You can do this now with method init_Pfeiffer("/dev/ttyUSB0")')
            return None

        self.init_Pfeiffer(port=port)
        return None

    def log(self,msg):
        '''messages to log file and to screen
        '''
        now=dt.datetime.utcnow()
        logmsg='%s | %s' % (now.strftime('%Y-%m-%d %H:%M:%S UT'),msg)
        h=open('hk_pfeiffer.log','a')
        h.write(logmsg+'\n')
        h.close()
        print(logmsg)
        return
                
    def init_Pfeiffer(self,port='/dev/pfeiffer'):
        '''initialize the power supply
        it should be recognized as /dev/powersupply or /dev/ttyACMn (n=0,1,2,...)
        
        it is usable by everyone because the following is in udev rules:

        SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6002", OWNER="qubic",
        GROUP="users", MODE="0666", SYMLINK+="pfeiffer"
        '''
        if not os.path.exists(port):
            self.log('ERROR! Device does not exist.')
            self.port=None
            self.device_ok=False
            return None
        self.port=port

        s=serial.Serial(port=port,timeout=0.1)
        self.s=s
        
        self.device_ok = True
        return True

    def send_command(self,cmd,ack=True):
        '''send a command and read the acknowledgement
        '''
        if not self.device_ok:
            self.log('ERROR! Device is not ok for commanding.')
            return False

        msg = '%s\r\n' % cmd
        try:
            self.s.write(msg)
        except:
            self.device_ok = False
            return False

        if not ack: return True
        
        reply = self.get_response()
        if reply=='\x06':
            return True
        return False

    def get_response(self):
        '''read from the pressure gauge
        '''
        if not self.device_ok:
            self.log('ERROR! Device is not ok for reading.')
            return None

        try:
            ans = self.s.readline()
        except:
            self.log('ERROR! Could not read device: %s' % self.port)
            return None

        return ans.strip()

    def read_pressure(self):
        '''send the command to read the pressure
        '''

        # command to request pressure gauge
        cmd = 'PR1'
        if not self.send_command(cmd,ack=True):
            return None

        # command to get the result
        cmd = '\x05'
        if not self.send_command(cmd,ack=False):
            return None
        
        response = self.get_response()
        val = response.split(',')

        # should have two values: status, and pressure
        if len(val)!=2:
            self.log('ERROR! Did not get expected response from the pressure gauge.')
            return None

        nak = self.get_response()
        if nak!='\x15':
            self.log('WARNING! Did not get NAK after pressure reading.')

        if val[0]!='0':
            self.log('ERROR! Pressure sensor data is not ok.')
            return None

        try:
            pressure = eval(val[1])
        except:
            self.log('ERROR! Unexpected response from pressure sensor: %s' % val[1])
            return None

        return pressure
    
        

        
        
        
