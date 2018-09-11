#!/usr/bin/env python
'''
$Id: arduino.py
$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
$created: Tue 29 May 2018 13:46:23 CEST
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

use the Arduino Uno as an ADC to monitor the signal generator

'''
from __future__ import division, print_function
import serial,time,multiprocessing
import numpy as np
from scipy.optimize import curve_fit
import datetime as dt
from satorchipy.datefunctions import *

def arduino_acquire(self,arduino_t,arduino_a):
    '''
    acquire data with timestamps from the Arduino Uno

    duration is given in seconds
    '''
    print('##### arduino_acquire #####')
    try:
        s=serial.Serial('/dev/arduino', 9600)
    except:
        print('Could not connect to the Arduino Uno')
        return None

    duration=self.tinteg
    if duration==None:
        dt_duration=dt.timedelta(minutes=5)
    else:
        dt_duration=dt.timedelta(seconds=duration)
        
    y=[]
    a=[]
    t=[]
    start_time=dt.datetime.utcnow()
    end_time=start_time+dt_duration
    now=dt.datetime.utcnow()
    while now < end_time:
        x=s.readline()
        now=dt.datetime.utcnow()
        y.append(x)
        t.append(dt.datetime.utcnow())


    print('started data acquisition at %s' %  t[0].strftime('%Y-%m-%d %H:%M:%S.%f UTC'))
    print('  ended data acquisition at %s' % t[-1].strftime('%Y-%m-%d %H:%M:%S.%f UTC'))
    delta=t[-1]-t[0]
    print('total acquisition time: %.3f seconds' % tot_seconds(delta))

    # the first reading is always blank
    for idx,val in enumerate(y):
        val_stripped=val.strip().replace('\r','')
        try:
            valno=eval(val_stripped)
            arduino_a.append(valno)
            arduino_t.append(t[idx])
        except:
            pass
        
    return arduino_t,arduino_a

def arduino_sin_curve(t,period,amplitude,offset,shift):
    '''
    the sine curve to fit to the modulated signal
    '''
    
    val=offset+amplitude*np.sin(2*np.pi*t/period  + shift)
    return val


def arduino_fit_signal(t,a,period=None,amplitude=None,offset=None,shift=None):
    '''
    fit the signal data to a sine curve
    '''

    # first guess
    if period is None:period=1.0
    if amplitude is None:
        amplitude=0.5*(max(a)-min(a))
    if offset is None:
        offset=amplitude+min(a)
    if shift is None: shift=0.0
    
    p0=[period,amplitude,offset,shift]
    popt,pcov=curve_fit(sin_curve,t,a,p0=p0)
    result={}
    result['period']=popt[0]
    result['amplitude']=popt[1]
    result['offset']=popt[2]
    result['shift']=popt[3]

    return result


def arduino_acquire_timeline(self,save=True,modulation=True):
    '''
    get a data timeline and the calibration source modulation at the same time

    this will replace integrate_scientific_data() and be moved to acquisition.py

    '''
    client = self.connect_QubicStudio()
    if client is None:return None

    if modulation:
        manager=multiprocessing.Manager()
        arduino_a=manager.list()
        arduino_t=manager.list()
    
        arduino_proc  = multiprocessing.Process(target=arduino_acquire, args=(self,arduino_t,arduino_a))
        arduino_proc.start()

    if not self.exist_timeline_data():self.tdata=[]
    tdata={}
    
    self.debugmsg('calling integrate_scientific_data for ASIC %i' % self.asic)
    self.debugmsg ('integration_time=%.2f' % self.tinteg)

    npixels=self.get_NPIXELS()
    tdata['NPIXSAMP']=npixels
    
    nsamples = self.get_nsamples()
    if nsamples is None: return None
    tdata['NSAMPLES']=nsamples
    
    period = self.sample_period()
    self.debugmsg('period=%.3f msec' % (1000*period))
    
    timeline_size = int(np.ceil(self.tinteg / period))
    self.debugmsg('timeline size=%i' % timeline_size)

    chunk_size=self.get_chunksize()
    if chunk_size is None: return None
    tdata['CHUNK']=chunk_size

    bias_config=self.get_bias()
    tdata['BIAS_MIN']=self.min_bias
    tdata['BIAS_MAX']=self.max_bias
    tdata['BIAS_MOD']=self.bias_frequency
    tdata['BIASMODE']=self.bias_mode
    
    timeline = np.empty((self.NPIXELS, timeline_size))

    # date of the observation
    self.assign_obsdate()
    tdata['DATE-OBS']=self.obsdate
    
    # bath temperature
    self.oxford_read_bath_temperature()
    tdata['TES_TEMP']=self.temperature

    # feedback loop resistance (relay)
    tdata['R_FEEDBK']=self.Rfeedback

    FLL_state,FLL_P,FLL_I,FLL_D=self.get_PID()
    tdata['FLL_STAT']=FLL_state
    tdata['FLL_P']=FLL_P
    tdata['FLL_I']=FLL_I
    tdata['FLL_D']=FLL_D
        
    # integration time
    tdata['INT-TIME']=self.tinteg

    # get the rawmask from which we calculate n_masked
    rawmask=self.get_RawMask()
    
    self.debugmsg('requesting scientific data timeline...')
    parameter = 'QUBIC_PixelScientificDataTimeLine_%i' % self.QS_asic_index
    req = client.request(parameter)
    self.debugmsg('scientific data requested.')
    istart = 0
    for i in range(int(np.ceil(timeline_size / chunk_size))):
        delta = min(chunk_size, timeline_size - istart)
        self.debugmsg('getting next data chunk...',level=2)
        timeline[:, istart:istart+delta] = req.next()[:, :delta]
        self.debugmsg('got data chunk.',level=2)
        istart += chunk_size
    req.abort()
    tdata['TIMELINE']=timeline


    if modulation:
        # get the timing info from the Arduino
        arduino_proc.join()

        tdata['MOD-AMP']=arduino_a
        tdata['MOD-TIME']=arduino_t
    
    if not self.AVOID_HANGUP:
        for count in range(10):
            req.abort() # maybe we need this more than once?
        del(req) # maybe we need to obliterate this?
        
    if save:self.tdata.append(tdata)
    return timeline
        



    

    
