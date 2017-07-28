"""
$Id: tools.py
$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>

     the following methods are originally by Michel Piat:
      set_VoffsetTES()
      set_slowDAC()
      set_diffDAC()
      get_amplitude()
      get_mean()
      integrate_scientific_data()


$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

tools which are generally useful for scripts using pystudio

"""
from __future__ import division, print_function
import numpy as np
import pystudio
import sys,os,time
import datetime as dt
import matplotlib.pyplot as plt
from glob import glob
import pickle
import pyfits

def connect_QubicStudio(self,client=None, ip=None):
    if ip==None:
        ip=self.QubicStudio_ip
    else:
        self.assign_QubicStudio_ip(ip)
    
    if client==None:
        client = pystudio.get_client()

    if client==None:
        print("connecting to QubicStudio on host: ",self.QubicStudio_ip)
        client = pystudio.DispatcherAccess(self.QubicStudio_ip, 3002)
        print('wait 3 seconds before doing anything')
        time.sleep(3)

    if not client.connected:
        print("ERROR: could not connect to QubicStudio")
        return None

    client.waitingForAckMode = True
    # client.sendSetScientificDataTfUsed(1) # data in Volts
    return client

def read_date_from_filename(self,filename):
    try:
        datestr=filename.split('_')[-1].split('.')[0]
        date=dt.datetime.strptime(datestr,'%Y%m%dT%H%M%SUTC')
    except:
        date=None
    return date

def write_fits(self):
    '''
    write data to file
    it could be timeline data or I-V data, or both
    '''
    datefmt='%Y%m%dT%H%M%SUTC'
    if self.obsdate==None:
        self.obsdate=dt.datetime.utcnow()
    datestr=self.obsdate.strftime(datefmt)

    prihdr = pyfits.Header()
    prihdr['TELESCOP']=('QUBIC','Telescope used for the observation')
    prihdr['OBSERVER']=(self.observer,'name of the observer')
    prihdr['DATE-OBS']=(self.obsdate.strftime('%Y-%m-%d %H:%M:%S UTC'),'date of the observation in UTC')
    prihdr['NSAMPLES']=(self.nsamples,'number of samples per integration time')
    prihdr['INT-TIME']=(self.tinteg,'integration time in seconds')
    prihdr['NPIXELS']=(self.NPIXELS,'number of TES detectors in the array')
    prihdr['ASIC']=(self.asic,'ASIC id (one quarter of the full QUBIC array)')
    prihdr['QUBIC-IP']=(self.QubicStudio_ip,'address of the QUBIC Local Control Computer')
    prihdr['NCYCLES']=(self.nbiascycles,'number of cycles of the Bias voltage')
    prihdr['CYCBIAS']=(self.cycle_vbias,'ramp return Bias, yes or no')
    prihdu = pyfits.PrimaryHDU(header=prihdr)

    if self.v_tes != None:
        fitsfile=str('QUBIC_TES_%s.fits' % datestr)
        if os.path.exists(fitsfile):
            print('file already exists! %s' % fitsfile)
            fitsfile=dt.datetime.utcnow().strftime('resaved-%Y%m%dT%H%M%SUTC__')+fitsfile
            print('instead, saving to file: %s' % fitsfile)

        nbias=len(self.vbias)
        fmtstr=str('%iD' % self.v_tes.shape[1])
        dimstr=str('%i' % self.v_tes.shape[0])
        #print('format=',fmtstr)
        #print('dim=',dimstr)
        col1  = pyfits.Column(name='V_tes', format=fmtstr, dim=dimstr, unit='ADU', array=self.v_tes)
        cols  = pyfits.ColDefs([col1])
        tbhdu1 = pyfits.BinTableHDU.from_columns(cols)

        col2  = pyfits.Column(name='V_bias',format='D', unit='V', array=self.vbias)
        cols  = pyfits.ColDefs([col2])
        tbhdu2 = pyfits.BinTableHDU.from_columns(cols)
        
        thdulist = pyfits.HDUList([prihdu, tbhdu1, tbhdu2])
        thdulist.writeto(fitsfile)

    if self.timelines != None:
        fitsfile=str('QUBIC_timeline_%s.fits' % datestr)
        if os.path.exists(fitsfile):
            print('file already exists! %s' % fitsfile)
            fitsfile=dt.datetime.utcnow().strftime('resaved-%Y%m%dT%H%M%SUTC__')+fitsfile
            print('instead, saving to file: %s' % fitsfile)

        ntimelines=self.timelines.shape[0]
        fmtstr=str('%iD' % self.timelines.shape[2])
        dimstr=str('%i' % self.timelines.shape[1])

        hdulist=[prihdu]
        for n in range(ntimelines):
            col1  = pyfits.Column(name='timelines', format=fmtstr, dim=dimstr, unit='ADU', array=self.timelines[n,:,:])
            cols  = pyfits.ColDefs([col1])
            tbhdu = pyfits.BinTableHDU.from_columns(cols)
            hdulist.append(tbhdu)
            
        thdulist = pyfits.HDUList(hdulist)
        thdulist.writeto(fitsfile)

    return

def read_fits(self,filename):
    if not isinstance(filename,str):
        print('ERROR! please enter a valid filename.')
        return None
    
    if not os.path.exists(filename):
        print('ERROR! file not found: %s' % filename)
        return None

    print('reading fits file: %s' % filename)
    h=pyfits.open(filename)
    nhdu=len(h)

    # check if it's a QUBIC file
    if nhdu<=1\
       or (not 'TELESCOP' in h[0].header.keys())\
       or (not h[0].header['TELESCOP'].strip()=='QUBIC'):
        print('This is not a QUBIC file.')
        return None

    self.observer=h[0].header['OBSERVER']
    self.obsdate=dt.datetime.strptime(h[0].header['DATE-OBS'],'%Y-%m-%d %H:%M:%S UTC')
    self.nsamples=h[0].header['NSAMPLES']
    if self.nsamples=='': self.nsamples=100 # data from 12/13 July 2017
    self.tinteg=h[0].header['INT-TIME']
    self.NPIXELS=h[0].header['NPIXELS']
    self.asic=h[0].header['ASIC']
    self.QubicStudio_ip=h[0].header['QUBIC-IP']

    if 'NCYCLES' in h[0].header.keys():
        self.nbiascycles=h[0].header['NCYCLES']

    if 'CYCBIAS' in h[0].header.keys():
        self.cycle_vbias=h[0].header['CYCBIAS']

    timelines=[]
    for hdu in h[1:]:
        hdrtype=hdu.header['TTYPE1']
        
        if hdrtype=='V_tes':
            '''
            this is I-V data
            '''
        
            # number of bias points
            nbias=eval(hdu.header['TFORM1'].strip()[:-1])

            # read the v_tes matrix
            data=hdu.data
            self.v_tes=np.empty((self.NPIXELS,nbias))
            for n in range(self.NPIXELS):
                self.v_tes[n,:]=data[n][0]

        if hdrtype=='V_bias':
            '''
            this is the bias points
            '''

            data=hdu.data
            self.vbias=np.empty(nbias)
            for n in range(nbias):
                self.vbias[n]=data[n][0]
            # check if this is cycled bias
            if self.nbiascycles>1:
                self.cycle_vbias=True
            else:
                self.cycle_vbias=False
            self.max_bias=max(self.vbias)
            self.min_bias=min(self.vbias)
            self.max_bias_position=np.argmax(self.vbias)
            

        if hdrtype=='timelines':
            '''
            this is the timeline data
            '''
            print('reading timeline data')
            data=hdu.data
            npts=eval(hdu.header['TFORM1'].strip()[:-1])
            timeline=np.empty((self.NPIXELS,npts))
            for n in range(self.NPIXELS):
                timeline[n,:]=data[n][0]
            timelines.append(timeline)
            

    # print('hdrtype=%s' % hdrtype)
    if hdrtype=='timelines':
        print('assigning timeline data')
        self.timelines=np.array(timelines)
    h.close()
    return

def get_amplitude(self,integration_time=None, asic=None):
    """
    Parameters
    ----------
    integration_time: float
    integration time, in seconds
    asic : int, optional
    ASIC number.
        
    """
    timeline = self.integrate_scientific_data(integration_time, asic)
    min_timeline = np.min(timeline, axis=-1)
    max_timeline = np.max(timeline, axis=-1)
    return max_timeline - min_timeline

def get_mean(self):
    """
    Parameters
    ----------
    integration_time: float
    integration time, in seconds
    asic : int, optional
    ASIC number.

    """
    timeline = self.integrate_scientific_data()
    return timeline.mean(axis=-1)

def integrate_scientific_data(self,integration_time=None,asic=None):
    client = self.connect_QubicStudio()
    if client==None:return None

    if not integrtion_time==None: self.assign_integration_time(integration_time)
    if not asic==None: self.assign_asic(asic)
    
    nsample = client.fetch('QUBIC_Nsample')
    print('nsample=',nsample)
    self.nsamples=nsample
    
    period = 1 / (2e6 / self.NPIXELS / nsample)
    print('period=',period)
    print ('integration_time=',self.tinteg)
    timeline_size = int(np.ceil(self.tinteg / period))
    chunk_size = client.fetch('QUBIC_PixelScientificDataTimeLineSize')
    timeline = np.empty((self.NPIXELS, timeline_size))
    parameter = 'QUBIC_PixelScientificDataTimeLine_{}'.format(self.asic_index())
    req = client.request(parameter)
    istart = 0
    for i in range(int(np.ceil(timeline_size / chunk_size))):
        delta = min(chunk_size, timeline_size - istart)
        timeline[:, istart:istart+delta] = req.next()[:, :delta]
        istart += chunk_size
    req.abort()
    return timeline

def set_VoffsetTES(self,tension, amplitude):
    client = connect_QubicStudio()
    if client==None:return None

    # conversion constant DAC <- Volts
    # A = 2.8156e-4
    A = 284.5e-6
    if tension > 0 and tension <= 9:
        DACoffset = tension / A - 1
    else:
        DACoffset = 65536 + tension / A
    DACoffset = int(np.round(DACoffset))
    print("DACoffset=%i" % DACoffset)

    if amplitude > 0 and amplitude <= 9:
        DACamplitude = amplitude / 0.001125 - 1
    else:
        DACamplitude = 65536 + amplitude / 0.001125
    DACamplitude = int(np.round(DACamplitude))
    client.sendSetCalibPolar(self.asic_index(), 1, 0, 99, DACamplitude, DACoffset)
    # wait and send the command again to make sure
    wait_a_bit()
    client.sendSetCalibPolar(self.asic_index(), 1, 0, 99, DACamplitude, DACoffset)
    return


def set_diffDAC(self,tension):
    client = connect_QubicStudio()
    if client==None:return None
    
    if tension > 0 and tension <= 3.5:
        diffDAC = tension / 2 / 7 * 65536 - 1
    else:
        diffDAC = 65536 * (1 + tension / 2 / 7)
    diffDAC = int(np.round(diffDAC))
    print('Setting diff DAC: ', diffDAC)
    client.sendSetDiffDAC(self.asic_index(), diffDAC)
    return



def set_slowDAC(self,tension):
    client = connect_QubicStudio()
    if client==None:return None
    
    if tension > 0 and tension <=3.5:
	slowDAC = tension / 1.4272e-4 - 1
    else:
	slowDAC = 65536 + tension / 1.4272e-4
        
    slowDAC = int(np.round(slowDAC))
    print('Setting slow DAC: ', slowDAC)
    client.sendSetSlowDAC(self.asic_index(), slowDAC)
    return



