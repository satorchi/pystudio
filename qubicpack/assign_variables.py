"""
$Id: assign_variables.py
$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
$created: Thu 13 Jul 2017 14:11:07 CEST
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

default values for various parameters in qubicpack

"""
from __future__ import division, print_function
import numpy as np
import pystudio
import sys,os,time
import datetime as dt
import matplotlib.pyplot as plt
from glob import glob

def assign_defaults(self):
    self.QubicStudio_ip='134.158.186.233'
    self.NPIXELS=128
    self.iv_axes=[-1,self.NPIXELS,-2.0,+2.0]
    self.figsize=(12.80,7.68)
    self.colours=['blue','green','red','cyan','magenta','yellow','black']
    self.asic=1
    self.tinteg=0.1
    self.v_tes=None
    self.vbias=None
    self.cycle_vbias=True
    self.pausetime=0.3
    self.obsdate=None
    self.observer='APC LaboMM'
    self.nsamples=None
    self.timelines=None
    return

def assign_observer(self,observer='APC LaboMM'):
    if not isinstance(observer,str):
        observer=str(observer)
    self.observer=observer
    return

def assign_asic(self,asic=1):
    if asic==None:asic=self.asic
    if not isinstance(asic,int):
        print('asic should have an integer value: 1 or 2.  assigning default asic=1')
        self.asic=1
    else:
        self.asic=asic
    return

def asic_index(self):
    return self.asic-1

def TES_index(self,TES=1):
    if (not isinstance(TES,int))\
       or TES<1\
       or TES>self.NPIXELS:
        print('TES should have a value between 1 and %i' % self.NPIXELS)
        print('assigning default: TES=1')
        TES=1
    TES_idx=TES-1
    return TES_idx
        

def assign_integration_time(self,tinteg=0.1):
    if tinteg==None:tinteg=self.tinteg
    if (not isinstance(tinteg,int))\
       and (not isinstance(tinteg,float))\
       and (tinteg<0.0):
        print('integration time should be a positive number of seconds.  Assigning default Tinteg=0.1')
        self.tinteg=0.1
    else:
        self.tinteg=tinteg
    return

def assign_Vtes(self,v_tes):
    if (not isinstance(v_tes,np.ndarray)):
        print('Please enter a 2 dimensional numpy array with the first dimension=%i' % self.NPIXELS)
        return None
    self.v_tes=v_tes
    return

def assign_pausetime(self,pausetime):
    if (not isinstance(pausetime,int)) and (not isinstance(pausetime,float)):
        print('pause time should be a number of seconds.  Assigning default pausetime=%.3f seconds' % self.pausetime)
    else:
        self.pausetime=pausetime
    return

    
def assign_ip(self,ip):
    if (not isinstance(ip,str)):
        print('please give an IP address for QubicStudio in the form xxx.xxx.xxx.xxx:')
        print('assigning default IP address: %s' % self.QubicStudio_ip)
        return None
    self.QubicStudio_ip=ip
    return

        
