#!/usr/bin/env python
'''
$Id: temperature_hk.py
$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
$created: Sun 09 Dec 2018 11:16:58 CET

$former_Id: cryo_data_logV2.py
$auth: Manuel Gonzalez

$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

get temperatures from the temperature diodes
'''
from __future__ import division, print_function
import os,sys,serial,subprocess
from glob import glob
import time
import datetime as dt
import struct
from shutil import copyfile
import numpy as np
from scipy import interpolate

class temperature_hk :
    ''' a class to gather temperatures from the temperature diodes
    there are 21 channels, of which 18 are used
    '''
    def __init__(self,port='/dev/cryo_temperatures',caldir=None,dumpraw=False):
 
        self.nchannel = 21
        self.nT = 18
        self.ser = None
        self.connected=False
        self.port=port
        self.dumpraw=dumpraw
        homedir='/home/pi'
        if 'HOME' in os.environ.keys():
            homedir=os.environ['HOME']
        data_subdir='data/temperature/data'
        cal_subdir='log_cryo/calibration'
        self.caldir='%s/%s/%s' % (homedir,data_subdir,cal_subdir)

        # these were the headings in the temperature.dat file
        self.labels=['T01_40K_filters',
                     'T09_shield_40K_down',
                     'T05_PT1_stage_1',
                     'T06_PT2_stage_1',
                     'T12_shield_40K_right',
                     'T02_4K_filters',
                     'T03_HWP1',
                     'T04_HWP2',
                     'T10_shield_4K_down',
                     'T11_shield_4K_right',
                     'T13_PT1_stage_2',
                     'T14_PT2_stage_2',
                     '300mK-4CP-D-1',
                     '300mK-4HS-D-1',
                     '300mK-3CP-D-1',
                     '300mK-3HS-D-1',
                     '1K-4HS-D-1',
                     '1K-4CP-D-1']

        self.connected=self.connect(port=port)
        res = self.setup_calibration(caldir)
        if not res: self.connected=False
        return None

    def log(self,msg):
        '''messages to log file and to screen
        '''
        now=dt.datetime.utcnow()
        logmsg='%s | %s' % (now.strftime('%Y-%m-%d %H:%M:%S UT'),msg)
        h=open('hk_temperature.log','a')
        h.write(logmsg+'\n')
        h.close()
        print(logmsg)
        return

    def connect(self,port=None):
        ''' connect by serial (USB) to the cryo temperature diode controller
        interface is defined in /etc/udev/rules.d/99-cryotemperature.rules
        '''
        if port is None: port=self.port
        self.port=port
        
        self.connected=False
        if not os.path.exists(port):
            self.log('ERROR! Could not find the temperature device: %s' % port)
            return False

        try:
            self.ser=serial.Serial(port=port, baudrate=19200, timeout=0.1)
        except:
            self.log('ERROR! Could not connect to the temperature device.')
            return False
        
        # wait for activation
        data_length = 0
        now=dt.datetime.utcnow()
        max_wait=dt.timedelta(seconds=30)
        wait_endtime=now+max_wait
        while data_length == 0 and now < wait_endtime:
	    string0 = self.device_readline()
            if string0 is None:
                return False
	    data_length = len(string0)
            now=dt.datetime.utcnow()

            if data_length == 0:
                self.log("ERROR! Timeout! Could not connect to cryo temperatures!")
                return False

        self.connected=True        
        return True

    def device_readline(self):
        '''read from the Temperature diodes, with error checking
        '''
        try:
            ans = self.ser.readline()
        except:
            self.log("Error! Couldn't read Temperature Diode data")
            return None

        # clean the datlist from possible crap.  Sometimes the diodes return '\x00' in the middle of the number
        ans = ans.replace('\x00','')
        return ans.strip()
    
            
    def disconnect(self):
        '''close the serial connection to the temperature diodes
        '''
        self.ser.close()
        self.connected=False
        return

    def setup_calibration(self,caldir=None):
        '''read the calibration tables
        '''
        if caldir is None:
            caldir=self.caldir
            
        if not os.path.isdir(caldir):
            self.log('ERROR! Could not find calibration directory: %s' % caldir)
            return False

        calibration_files = map(lambda x: caldir+'/calibration_ch'+str(x).zfill(2)+'.dat',range(self.nT))
        # check for file existence
        for fname in calibration_files:
            if not os.path.exists(fname):
                self.log('ERROR! Could not find calibration file: %s' % fname)
                return False    
        self.calibration_tables = map(lambda x: np.loadtxt(x),calibration_files)

        self.gain=[0.0626158803,
                   0.0626095353,
                   0.0626137451,
                   0.0626129561,
                   0.0626046339,
                   0.0626023651,
                   0.0626006617,
                   0.0626026485,
                   0.0625785803,
                   0.0625785839,
                   0.0625793290,
                   0.0625781058,
                   0.0625662881,
                   0.0625695137,
                   0.0625704064,
                   0.0625677486,
                   0.0626280689,
                   0.0626252146,
                   0.0626282954,
                   0.0626263287]

        self.offset=[-2049.6181153598,
                     -2049.9601678205,
                     -2049.2013364949,
                     -2049.6533307630,
                     -2049.2122546909,
                     -2049.2859049597,
                     -2049.5080966974,
                     -2049.0869777510,
                     -2048.5491308714,
                     -2048.5516331324,
                     -2048.5804165382,
                     -2048.4528778901,
                     -2048.5684350553,
                     -2048.4054581436,
                     -2048.3698491680,
                     -2048.3218114873,
                     -2050.3137988660,
                     -2050.2215204946,
                     -2050.2695627877,
                     -2050.0539409956]

        # corrected offsets measured Mon 21 Jan 2019 16:37:01 CET (MP & SAT @ APC)
        #self.offset[0] -= -632.621
        #self.offset[1] -=  370.963

        
        return True

    def get_temperatures(self):
        '''read the temperatures from the diodes
        '''

        if self.ser is None:
            self.log('ERROR! Please setup the Temperature Diode device.  run connect()')
            return None
        
        voltageData = []
        temperatureData = []

        a = self.device_readline()
        if a is None: return None
        data_length = len(a)
        if data_length == 0:
            self.log('ERROR! Temperature diodes returned data length 0')
            return None

        datlist = a.split()
        npts = len(datlist)
        
        if npts<=self.nT:
            self.log('Insufficient data.  length=%i, rawData: %s' % (npts,datlist))
            return None

        try:
            rawData = map(int,datlist)
            #self.log('temperature diode rawData length = %i' % len(rawData))
        except:
            self.log('ERROR! Bad reply from Temperature diodes: npts=%i, datlist=%s' % (npts,datlist))
            return None
        
        for idx in range(self.nT):
            voltageData.append(rawData[idx+1]*self.gain[idx]+self.offset[idx])
            x=self.calibration_tables[idx][:,0]
            y=self.calibration_tables[idx][:,1] 
            interpolate_function = interpolate.interp1d(x,y,kind='linear',fill_value='extrapolate')
            temperatureData.append(interpolate_function(voltageData[idx]))

        if self.dumpraw:
            self.dump_rawData(rawData,voltageData)

        return np.array(temperatureData)
    

    def dump_rawData(self,rawData,voltageData):
        '''dump the uncalibrated data to file
        '''
        npts = len(rawData) # this should be 21
        fmt = '%6i'
        for idx in range(npts-1):
            fmt += ' %6i'
        fmt += '\n'
        h=open('TEMPERATURE_RAW.txt','a')
        h.write(fmt % tuple(rawData))
        h.close()

        npts = len(voltageData) # this should be 18
        fmt = '%.3f'
        for idx in range(npts-1):
            fmt += ' %.3f'
        fmt += '\n'
        h=open('TEMPERATURE_VOLT.txt','a')
        h.write(fmt % tuple(voltageData))
        h.close()        
        return
