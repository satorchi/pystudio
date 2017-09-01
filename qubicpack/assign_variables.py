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
import sys,os,time
import datetime as dt
import matplotlib.pyplot as plt
from glob import glob

def assign_defaults(self):
    self.debuglevel=0
    self.zero=1e-9
    self.QubicStudio_ip='134.158.186.233'
    self.NPIXELS=128
    self.kBoltzmann=1.3806485279e-23
    self.Rshunt=10.e-3 # 10mOhm, mail from M.Piat to M.Salatino 2017-08-10
    self.Rbias =10.e3  # 10kOhm, mail from M.Piat to M.Salatino 2017-08-10
    self.figsize=(12.80,7.68)
    self.colours=['blue','green','red','cyan','magenta','yellow','black']
    self.assign_asic(1)
    self.tinteg=0.1
    self.adu=None
    self.vbias=None
    self.cycle_vbias=True
    self.nbiascycles=None
    self.max_bias=None
    self.min_bias=None
    self.max_bias_position=None
    self.pausetime=0.3
    self.obsdate=None
    self.endobs=None
    self.observer='APC LaboMM'
    self.nsamples=None
    self.timelines=None
    self.assign_pix_grid()
    self.assign_pix2tes()
    self.filtersummary=[]
    for idx in range(self.NPIXELS): self.filtersummary.append(None)
    self.assign_lookup_table()
    self.temperature=None
    return

def assign_observer(self,observer='APC LaboMM'):
    if not isinstance(observer,str):
        observer=str(observer)
    self.observer=observer
    return

def assign_asic(self,asic=1):
    if asic==None:asic=self.asic
    if not isinstance(asic,int) or asic<1 or asic>2:
        print('asic should have an integer value: 1 or 2.  assigning default asic=1')
        self.asic=1
    else:
        self.asic=asic


    ######### Is this correct?
    #### QubicStudio has a reverse nomenclature for the ASIC index
    #### compared to the translation tables (eg. Correspondance.xlsx)
    # so define here a specific QubicStudio ASIC index which should be used in the acquisition methods
    # see, for example, integrate_scientific_data() in tools.py
    asic_index=self.asic_index()
    #self.QS_asic_index=asic_index
    if asic_index==0:
        self.QS_asic_index=1
    else:
        self.QS_asic_index=0

    # Wed 02 Aug 2017 15:48:15 CEST
    # during lab tests, QubicStudio is always using asic_index=0
    # we change the asic by physically switching a cable to another connector
    #self.QS_asic_index=0
    # Fri 04 Aug 2017 13:38:10 CEST
    # in fact, we should change a jumper on the FPGA board to change the ID of the ASIC
    
    return

def asic_index(self):
    return self.asic-1

def TES_index(self,TES):
    if (not isinstance(TES,int))\
       or TES<1\
       or TES>self.NPIXELS:
        print('TES should have a value between 1 and %i' % self.NPIXELS)
        return None
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

def assign_ADU(self,adu):
    if (not isinstance(adu,np.ndarray)):
        print('Please enter a 2 dimensional numpy array with the first dimension=%i' % self.NPIXELS)
        return None
    self.adu=adu
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


def assign_temperature(self,temp):
    if (not isinstance(temp,int)) and (not isinstance(temp,float)):
        print('ERROR! Temperature should be a number in Kelvin (not milliKelvin)')
        self.temperature=None
        return None
    else:
        self.temperature=temp
    return self.temperature
