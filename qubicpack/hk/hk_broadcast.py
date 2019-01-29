#!/usr/bin/env python
'''
$Id: hk_broadcast.py
$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
$created: Mon 03 Dec 2018 15:23:50 CET
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

class for broadcasting/receiving QUBIC Housekeeping data
'''
from __future__ import division, print_function
import sys,os,subprocess,time,socket,struct
import numpy as np
import datetime as dt
import re

from qubicpack.hk.powersupply import PowerSupply, PowerSupplies, known_supplies
from qubicpack.hk.entropy_hk import entropy_hk
from qubicpack.hk.temperature_hk import temperature_hk
from qubicpack.hk.pfeiffer import Pfeiffer

class hk_broadcast :
    '''a class for broadcasting  and receiving QUBIC housekeeping data
    '''

    def __init__(self):
        self.BROADCAST_PORT = 4005
        self.RECEIVER = '<broadcast>'      # server broadcasts
        self.RECEIVER = '134.158.187.21'   # server sends only to QubicStudio
        self.RECEIVER = '134.158.187.224'   # server sends only to QubicStudio
        #self.RECEIVER = '134.158.187.0/24' # server broadcasts to APC subnet (syntax no good)
        self.RECEIVER = '192.168.2.8' # QubicStudio on the QUBIC private network
        self.LISTENER = ''          # client listens on ethernet device (usually eth0)
        self.LISTENER = '127.0.0.1' # client listens on localhost
        self.sampling_period = 2.0
        self.nENTROPY_TEMPERATURE = 8
        self.nMECH = 2
        self.nHEATER = 6
        self.nPRESSURE = 1
        self.record = self.define_hk_record()
        self.hk_entropy = None
        self.powersupply = None
        self.hk_temperature = None
        self.dump_diode_rawData = True
        self.hk_pressure = None
        return None

    def millisecond_timestamp(self):
        '''return the current date in milliseconds since 1970-01-01 in UT
        '''
        now=dt.datetime.utcnow()
        msec=now.strftime('%f')[0:3]
        tstamp=int('%s%s' % (now.strftime('%s'),msec))
        return tstamp

    def current_timestamp(self):
        '''return the current date in milliseconds since 1970-01-01 in UT
        '''
        now=dt.datetime.utcnow()
        tstamp=float(now.strftime('%s.%f'))
        return tstamp
    
    def define_hk_record(self):
        '''define a housekeeping data record
        '''
        dummy_val=1000
        
        # packet identifiers
        STX=0xAA
        ID=1

        # make the data record
        names=[]
        fmts=[]
        record_zero=[]

        # identifiers
        names.append('STX')
        fmts.append('i1')
        record_zero.append(STX)

        names.append('QUBIC_ID')
        fmts.append('i1')
        record_zero.append(ID)

        # the current date (milliseconds since 1970-1-1)
        # the current date (seconds since 1970-1-1)
        names.append('DATE')
        fmts.append('f8')
        record_zero.append(self.current_timestamp())

        # temperatures from the two AVS47 controllers
        for idx in range(2):
            avs='AVS47_%i' % (idx+1)
            for ch in range(8):
                recname='%s_ch%i' % (avs,ch)
                names.append(recname)
                fmts.append('f8')
                record_zero.append(dummy_val)
                dummy_val+=1

        # the Mechanical Heat Switch positions
        for idx in range(2):
            mhs='MHS%i' % (idx+1)
            names.append(mhs)
            fmts.append('i4')
            record_zero.append(dummy_val)
            dummy_val+=1

        # the power supplies (heaters)
        for meastype in ['Volt','Amp']:
            for idx in range(8):
                heater='HEATER%i' % (idx+1)
                names.append('%s_%s' % (heater,meastype))
                fmts.append('f8')
                record_zero.append(dummy_val)
                dummy_val+=1

        # the pressure sensor
        for idx in range(8):
            pressure_sensor='PRESSURE%i' % (idx+1)
            names.append('%s' % pressure_sensor)
            fmts.append('f8')
            record_zero.append(dummy_val)
            dummy_val+=1

        # the temperature diodes
        for idx in range(21): # THIS MUST CHANGE TO 21 AFTER WILFRIED CHANGES QUBICSTUDIO
            Tname='TEMPERATURE%02i' % (idx+1)
            names.append('%s' % Tname)
            fmts.append('f8')
            record_zero.append(dummy_val)
            dummy_val+=1

        ########### we don't send the labels themselves ###########
        # names=['LABELS']+names
        # names_line=','.join(names)
        # fmts=['a%i' % len(names_line)]+fmts
        # fmts_line=','.join(fmts)
        # record_zero=[names_line]+record_zero

        names_line=','.join(names)
        fmts_line=','.join(fmts)
        record=np.recarray(names=names_line,formats=fmts_line,shape=(1))
        for idx,val in enumerate(record_zero):
            record[0][idx]=val
        return record

    def get_entropy_hk(self):
        '''sample the housekeeping from the entropy (Major Tom) controller
        '''
        if self.hk_entropy is None:
            self.hk_entropy = entropy_hk()

        if not self.hk_entropy.connected:
            self.log('ERROR! Major Tom is not responding.')
            return None

        # temperatures from the two AVS47 controllers
        for idx in range(2):
            avs='AVS47_%i' % (idx+1)
            for ch in range(self.nENTROPY_TEMPERATURE):
                recname='%s_ch%i' % (avs,ch)
                tstamp,dat=self.hk_entropy.get_temperature(dev=avs,ch=ch)
                if tstamp is None:
                    tstamp=self.current_timestamp()
                if dat is None:
                    self.record[recname][0]=-1
                else:
                    self.record[recname][0]=dat
                    self.log_hk(recname,tstamp,dat)
                

        # the Mechanical Heat Switch positions
        for idx in range(self.nMECH):
            ch=idx+1
            recname='MHS%i' % ch
            dat=self.hk_entropy.mech_get_position(ch)
            tstamp=self.current_timestamp()
            if dat is None:
                self.record[recname][0]=-1
            else:
                self.record[recname][0]=dat
                self.log_hk(recname,tstamp,dat)

        return self.record

    def get_powersupply_hk(self):
        '''sample the housekeeping data from the TTi power supplies
        '''

        if self.powersupply is None:
            self.powersupply=PowerSupplies()

        # the power supplies (heaters)
        for idx in range(self.nHEATER):
            heater='HEATER%i' % (idx+1)
            cmd='%s readings' % heater
            argv=cmd.split()
            cmd=self.powersupply.parseargs(argv)
            dat=self.powersupply.runCommands(cmd)
            if not dat or isinstance(dat,str) or len(dat)!=3 or isinstance(dat[0],str) or isinstance(dat[1],str):
                self.log('ERROR! Strange reply from power supply: %s' % str(dat))
                dat = None
                

            # if no data (maybe powersupply not connected) return -1 and do not log
            for _idx,meastype in enumerate(['Volt','Amp']):
                recname='%s_%s' % (heater,meastype)
                tstamp=self.current_timestamp()
                if dat is None:
                    self.record[recname][0] = -1
                else:
                    try:
                        status = dat[-1]
                        self.record[recname][0]=dat[_idx]
                        self.log_hk(recname,tstamp,dat[_idx],status)
                    except:
                        self.record[recname][0] = -1
                        self.log('ERROR! Unable to interpret answer from power supply: %s' % dat)
                        
                    

        return self.record

    def get_temperature_hk(self):
        '''sample housekeeping data from the temperature diodes
        '''
        data_ok = True

        if self.hk_temperature is None:
            self.hk_temperature=temperature_hk(dumpraw=self.dump_diode_rawData)

        if not self.hk_temperature.connected:
            # try to reconnect
            self.hk_temperature.connect()
            
        if not self.hk_temperature.connected:
            self.log('ERROR! Temperature diodes not communicating')
            data_ok = False
            temperatures = -np.ones(self.hk_temperature.nT)
        else:
            temperatures = self.hk_temperature.get_temperatures()

        if temperatures is None:
            self.log('ERROR! Bad reply from Temperature diodes')
            temperatures = -np.ones(self.hk_temperature.nT)
            data_ok = False
            
        for idx,val in enumerate(temperatures):
            recname = 'TEMPERATURE%02i' % (idx+1)
            tstamp = self.current_timestamp()
            self.record[recname][0] = val
            if data_ok: self.log_hk(recname,tstamp,val)
                    
        return self.record

    def get_pressure_hk(self):
        '''get the pressure data
        '''
        if self.hk_pressure is None:
            self.hk_pressure=Pfeiffer(port='/dev/pfeiffer')

        # the pressure gauge (this should be expanded into a loop for multiple pressure gauges)
        gauge = 'PRESSURE1'
        dat = self.hk_pressure.read_pressure()
        if not dat or isinstance(dat,str):
            self.log('ERROR! Strange reply from power supply: %s' % str(dat))
            dat = None
                
        # if no data (maybe gauge not connected) return -1 and do not log
        recname='%s' % gauge
        tstamp=self.current_timestamp()
        if dat is None:
            self.record[recname][0] = -1
        else:
            self.record[recname][0] = dat
            self.log_hk(recname,tstamp,dat)                    

        return self.record
    
    def get_all_hk(self):
        '''sample all the housekeeping from the various sensors
        '''
        self.get_entropy_hk()
        self.get_powersupply_hk()
        self.get_temperature_hk()
        self.get_pressure_hk()
        self.record[0].DATE = self.current_timestamp()
        return self.record

    def unpack_data(self,data):
        '''unpack the received data packet
        '''
        fmt_translation={}
        fmt_translation['int8']    = 'b'
        fmt_translation['int16']   = 'h'
        fmt_translation['int32']   = 'i'
        fmt_translation['int64']   = 'q'
        fmt_translation['float32'] = 'f'
        fmt_translation['float64'] = 'd'

        names=self.record.dtype.names
        fmt='<'
        for name in names:
            key = str(self.record.dtype[name])
            fmt+=fmt_translation[key]

        data_tuple = struct.unpack(fmt,data)
        self.record[0] = data_tuple
        return self.record

        
    def hk_client(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        client.bind((self.LISTENER, self.BROADCAST_PORT))
        if self.LISTENER=='':
            listener = 'all'
        else:
            listener = self.LISTENER
            
        self.log('client listening on %s' % listener)
        nbytes=self.record.nbytes
        local_counter=0
        while True:
            data, addr = client.recvfrom(nbytes)
            self.unpack_data(data)
            self.log_record()
            timestamp_date=dt.datetime.fromtimestamp(1e-3*self.record.DATE[0]).strftime('%Y-%m-%d %H:%M:%S UT')
            msg='client %08i: received timestamp: %s' % (local_counter,timestamp_date)
            self.log(msg)
            local_counter+=1
    
        return local_counter


    def hk_server(self,test=False,eth=None):
        '''broadcast all housekeeping info
        '''

        if eth is None:
            cmd='/sbin/ifconfig -a'
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            out,err=proc.communicate()
            devs=[]
            for line in out.split('\n'):
                match=re.match('^(eth[0-9])',line)
                if match:
                   devs.append(match.groups()[0])
            if devs:
                eth=devs[-1]
            else:
                eth='lo'

            
        cmd='/sbin/ifconfig %s' % eth
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out,err=proc.communicate()
        for line in out.split('\n'):
            if line.find('inet ')>0: break
        hostname=line.split()[1]
        self.log('server: hostname=%s' % hostname)
        self.log('server: receiver=%s' % self.RECEIVER)
        now=dt.datetime.utcnow()
        stoptime=now+dt.timedelta(days=1000)

        if test:
            hostname='127.0.0.1' # for testing
            self.RECEIVER='127.0.0.1'
            self.log('server: hostname=%s for testing' % hostname)
            stoptime=now+dt.timedelta(minutes=5)


        s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.settimeout(0.2)
        s.bind((hostname,15000))
        
        msg=self.record
        counter=0
        while now < stoptime:


            if not test:
                msg=self.get_all_hk()
            else:
                msg[0].DATE=self.current_timestamp()
            s.sendto(msg, (self.RECEIVER, self.BROADCAST_PORT))

            ###################################################################################
            #### we do not log the record here.  It is done by the get_<controller>_hk() methods
            # self.log_record()
            ###################################################################################
            
            time.sleep(self.sampling_period)
            now=dt.datetime.utcnow()
            counter+=1

        s.close()
        return


    def log_hk(self,rootname,tstamp,data,data2=None):
        '''add data to log file
        '''

        # if no data, return quietly
        if data is None:return False

        # override timestamp.  This corrects the start/stop timestamping by Entropy
        tstamp = self.current_timestamp()

        try:
            if data2 is None:
                line = '%f %e\n' % (tstamp,data)
            else:
                line = '%f %e %s\n' % (tstamp,data,str(data2))
        except:
            self.log('ERROR! Could not convert timestamp,data for log_hk()')
            return False
        
        filename='%s.txt' % rootname
        h=open(filename,'a')
        h.write(line)
        h.close()
        return True

    def log_record(self):
        '''put the housekeeping data in log files
        '''

        # filenames take from record names.  We skip the first three: STX,QUBIC_ID,DATE
        names=self.record.dtype.names[3:]
        tstamp=self.record.DATE[0]
        for idx,name in enumerate(names):
            dat=self.record.field(idx+3)[0]
            self.log_hk(name,tstamp,dat)
        return True

    def log(self,msg):
        '''messages to log file and to screen
        '''
        now=dt.datetime.utcnow()
        logmsg='%s | %s' % (now.strftime('%Y-%m-%d %H:%M:%S UT'),msg)
        h=open('hk_broadcast.log','a')
        h.write(logmsg+'\n')
        h.close()
        print(logmsg)
        return
    
### end of hk_broadcast class definition



