#!/usr/bin/env python
'''
$Id: timeline.py
$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
$created: Tue 17 Oct 2017 19:04:04 CEST
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

utilities for QUBIC TES timeline data
'''
from __future__ import division, print_function
import numpy as np
import sys,os,time
import datetime as dt
import matplotlib.pyplot as plt

def exist_timeline_data(self):
    '''
    check if we have timeline data
    '''
    if not isinstance(self.timelines,list):
        return False
    if len(self.timelines)==0:
        return False
    if not isinstance(self.timelines[0],np.ndarray):
        return False
    return True

def amplitude2DAC(self,amplitude):
    '''
    convert bias voltage amplitude in Volts to DAC to send to QubicStudio
    '''
    if amplitude > 0 and amplitude <= 9:
        # DACamplitude = amplitude / 0.001125 - 1
        DACamplitude = amplitude / 0.001125  # "-1" removed Tue 17 Oct 2017 14:09:47 CEST
    else:
        DACamplitude = 65536 + amplitude / 0.001125
    DACamplitude = int(np.round(DACamplitude))
    return DACamplitude

def bias_offset2DAC(self,bias):
    '''
    convert bias offset voltage in Volts to DAC to send to QubicStudio
    '''

    # conversion constant DAC <- Volts
    # A = 2.8156e-4
    A = 284.5e-6
    if bias > 0 and bias <= 9:
        # DACoffset = bias / A - 1
        DACoffset = bias / A # "-1" removed Tue 17 Oct 2017 15:47:03 CEST
    else:
        DACoffset = 65536 + bias / A
    DACoffset = int(np.round(DACoffset))
    self.debugmsg("DACoffset=%i" % DACoffset)
    return DACoffset

def sample_period(self):
    '''
    the integration time per sample.  This is in seconds.
    '''
    if self.nsamples==None:return None
    period = 1.0 / (2e6 / self.NPIXELS / self.nsamples)
    return period

def timeline_npts(self):
    '''
    the size of the timeline determined from requested parameters.
    This is the number of points in the timeline vector
    '''
    sample_period=self.sample_period()
    if sample_period==None:return None
    timeline_size = int(np.ceil(self.tinteg / sample_period))
    return timeline_size

def plot_timeline(self,n=None):
    '''
    plot the timeline
    '''
    if not self.exist_timeline_data():
        print('ERROR! No timeline data.')
        return None

    if not isinstance(n,int):
        # by default, plot the first one.  this could change
        n=0

    ntimelines=len(self.timelines)
    if n>=ntimelines:
        print('Please enter a timeline between 0 and %i' % (ntimelines-1))
        return None

    sample_period=self.sample_period()
    timeline_npts = self.timeline_npts()
    time_axis=sample_period*np.arange(timeline_npts)
    current=self.ADU2I(self.timelines[n])

    
    if isinstance(self.obsdates,list) and len(self.obsdates)==ntimelines:
        timeline_date=self.obsdates[n]
    else:
        timeline_date=self.obsdate
    
    ttl=str('QUBIC Timeline curve for TES#%3i (%s)' % (TES,timeline_date.strftime('%Y-%b-%d %H:%M UTC')))

    if self.temperature==None:
        tempstr='unknown'
    else:
        tempstr=str('%.0f mK' % (1000*self.temperature))
    subttl=str('ASIC #%i, Pixel #%i, Temperature %s' % (self.asic,self.tes2pix(TES),tempstr))
    
    if xwin: plt.ion()
    else: plt.ioff()

    fig=plt.figure(figsize=self.figsize)
    fig.canvas.set_window_title('plt: '+ttl) 
    fig.suptitle(ttl+'\n'+subttl,fontsize=16)
    ax=plt.gca()
    ax.set_xlabel('time  /  seconds')
    ax.set_ylabel('Current  /  $\mu$A')
    

    
    
    return
