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

def calsource_init(self,source=None):
    '''
    setup communication to the Low Frequency source
    '''
    if source==None:
        print('Please enter the calibration source: HF or LF')
        return None

    if source.upper()=='LF':
        dev='/dev/calsource-LF'
        which_freq='Low'
    else:
        dev='/dev/calsource-HF'
        which_freq='High'
        
    if not os.path.exists(dev):
        print('ERROR! could not connect to the %s Frequency Calibration Source.' % which_freq)
        return None

    connection=serial.Serial(dev)
    return connection

def calsource_setFreqCommand(self,f):
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

def calsource_outputFrequency(self,response):
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
    return (s+response[0])*24


def calsource_setFrequency(self,f=None,source=None):
    '''
    set the frequency.  Note that this will send the command to the device.
    the method above calsource_setFreqCommand() only formats the command without sending
    '''

    if source==None:
        print('Please enter the calibration source: HF or LF')
        return None

    if source.upper()=='HF':        
        factor=24.
        com=self.calsource_HF
        if self.calsource_HF==None:
            self.calsource_HF=self.calsource_init('HF')
            if self.calsource_HF==None:return None

    elif source.upper()=='LF':
        factor=12.
        com=self.calsource_LF
        if self.calsource_LF==None:
            self.calsource_LF=self.calsource_init('LF')
            if self.calsource_LF==None:return None

    else:
        print('ERROR! Please enter a valid calibration source: HF or LF')
        return None

    cmd=self.calsource_setFreqCommand(f/factor)
    com.write(cmd)
    response=bytearray(com.read(6))

    if(response[0]==85):
        of=self.calsource_outputFrequency(response[1:])
    else:
        print("communication error")
        of=calsource_outputFrequency(response[1:])
    
    print('The output frequency is %.3f GHz' % of)
    return of


    

        
    
