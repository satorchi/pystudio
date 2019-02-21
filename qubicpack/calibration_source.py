'''
$Id: calibration_source.py
$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
       Manuel Gonzalez <manuel.gonzalez@ib.edu.ar>

$created: Tue 03 Oct 2017 19:18:51 CEST
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

send commands to the QUBIC calibration source

see documentation in:
 Tx 263 130-170GHz User Guide.pdf
 Tx 264 190-245GHz User Guide.pdf

udev rules should be setup in order to identify the calibration source
the udev rules can be found in the scripts directory of pystudio
and also here.  

save the following in file /etc/udev/rules.d/calibration-source.rules

ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", ATTRS{serial}=="VDIE0032", ACTION=="add", OWNER="qubic", GROUP="users", MODE="0644", SYMLINK+="calsource-HF"

ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", ATTRS{serial}=="VDIE0031", ACTION=="add", OWNER="qubic", GROUP="users", MODE="0644", SYMLINK+="calsource-LF"


'''
from __future__ import division, print_function
import os,serial
import numpy as np

import readline
readline.parse_and_bind('tab: complete')
readline.parse_and_bind('set editing-mode vi')

class calibration_source:
    '''
    a class to communicate with the calibration sources
    '''

    def __init__(self,source=None):
        self.s = None
        self.port = None
        self.calsource = None
        self.init(source=source)
        return None

    def init(self,source=None):
        '''
        setup communication to the calibration source
        '''
        self.clear_connection()

        if source is None:
            source = self.calsource
        
        if source is None:
            print('Please enter the calibration source: HF or LF')
            return None

        if source.upper()=='LF':
            dev='/dev/calsource-LF'
            which_freq='Low'
            self.calsource = 'LF'
            self.factor = 12.
        else:
            dev='/dev/calsource-HF'
            which_freq='High'
            self.calsource = 'HF'
            self.factor = 24.

        
        if not os.path.exists(dev):
            print('ERROR! No device for the %s Frequency Calibration Source.' % which_freq)
            return None

        try:
            self.s = serial.Serial(dev,timeout=0.5)
            self.port = dev
        except:
            print('ERROR! could not connect to the %s Frequency Calibration Source.' % which_freq)
            self.s = None
        return

    def clear_connection(self):
        '''
        clear a stale connection
        this could be called by set_Frequency()
        '''
        self.s = None
        self.port = None
        return

    def is_connected(self):
        '''
        check if the calibration source is connected
        '''
        if self.s is None:
            return False

        if self.port is None:
            return False

        if not os.path.exists(self.port):
            self.clear_connection()
            return False
        
        return True

    
    def set_FreqCommand(self,f):
        '''
        make the frequency command
        this code by Manuel Gonzalez
        '''
        a=[6,70]
        for i in range(5):
            a.append(int(f))
            f=f % 1
            f*=256
        b=a[0]
        for i in a[1:]:
            b=b^i
        a.append(b)
        c = bytearray(a)
        return c

    def output_Frequency(self,response):
        '''
        interpret the result of the output from the calibration source
        this code by Manuel Gonzalez
        '''

        # make sure we have a bytearray
        if not isinstance(response,bytearray):
            response=bytearray(response)

        # interpret the result
        result = ''
        for i in response[1:]:
            result+=format(i,'08b') 
            j=1
            s=0
            for i in result:
                if(int(i)):
                    s+=2**(-j)
                j+=1
        return (s+response[0])


    def set_Frequency(self,f):
        '''
        this is a wrapper to send the frequency command.
        we add the possibility to try twice in case we lost contact with the device
        '''
        of = self.send_set_Frequency(f)
        if of is None:
            of = self.send_set_Frequency(f)

        return of
    

    def send_set_Frequency(self,f):
        '''
        set the frequency.  Note that this will send the command to the device.
        the method set_FreqCommand() only formats the command without sending
        '''

        if self.calsource is None:
            print('Please initialize the calibration source')
            return None

        if not self.is_connected():
            print('initializing calibration source %s' % self.calsource)
            self.init(source=self.calsource)

        if not self.is_connected():
            return None
            
        
        cmd=self.set_FreqCommand(f/self.factor)
        try:
            self.s.write(cmd)
        except:
            print("Communication error: Could not send command.")
            self.clear_connection()
            return None

        try:
            response=bytearray(self.s.read(6))
        except:
            print("Communication error:  Could not receive response.")
            self.clear_connection()
            return None

        if(response[0]==85):
            of=self.output_Frequency(response[1:])
        else:
            print("Communication error:  Invalid response.")
            self.clear_connection()
            return None
    
        print('The output frequency is %.3f GHz' % of)
        return of

    def set_default_settings(self):
        '''
        set default settings
        '''
        if self.calsource == 'LF':
            freq = 150.0

        if self.calsource == 'HF':
            freq = 220.0

        of = self.set_Frequency(freq)
        return of
    

    

        
    
