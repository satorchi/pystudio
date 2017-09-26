'''
$Id: acquisition.py
$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
$created: Mon 07 Aug 2017 07:35:33 CEST
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

acquisition methods.  These require a connection to QubicStudio

     the following methods are originally by Michel Piat:
      set_VoffsetTES()
      set_slowDAC()
      set_diffDAC()
      get_amplitude()
      get_mean()
      integrate_scientific_data()

'''
from __future__ import division, print_function
import numpy as np
import pystudio
import sys,os,time
import datetime as dt
import matplotlib.pyplot as plt
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

def get_amplitude(self):
    """
    Parameters
    ----------
    integration_time: float
    integration time, in seconds
    asic : int, optional
    ASIC number.
        
    """
    timeline = self.integrate_scientific_data()
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

def integrate_scientific_data(self):
    client = self.connect_QubicStudio()
    if client==None:return None

    self.debugmsg('calling integrate_scientific_data for ASIC %i' % self.asic)
    
    integration_time=self.tinteg
    asic=self.asic
    
    
    nsample = client.fetch('QUBIC_Nsample')
    # QubicStudio returns an array of integer of length 1.
    # convert this to a simple integer
    nsample = int(nsample)
    self.debugmsg('nsample=%i' % nsample)
    self.nsamples=nsample
    
    period = 1 / (2e6 / self.NPIXELS / nsample)
    self.debugmsg('period=%.3f msec' % (1000*period))
    self.debugmsg ('integration_time=%.2f' % self.tinteg)
    timeline_size = int(np.ceil(self.tinteg / period))
    chunk_size = client.fetch('QUBIC_PixelScientificDataTimeLineSize')
    timeline = np.empty((self.NPIXELS, timeline_size))
    parameter = 'QUBIC_PixelScientificDataTimeLine_{}'.format(self.QS_asic_index)
    req = client.request(parameter)
    istart = 0
    for i in range(int(np.ceil(timeline_size / chunk_size))):
        delta = min(chunk_size, timeline_size - istart)
        timeline[:, istart:istart+delta] = req.next()[:, :delta]
        istart += chunk_size
    req.abort()
    return timeline

def set_VoffsetTES(self,tension, amplitude):
    client = self.connect_QubicStudio()
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
    client.sendSetCalibPolar(self.QS_asic_index, 1, 0, 99, DACamplitude, DACoffset)
    # wait and send the command again to make sure
    self.wait_a_bit()
    client.sendSetCalibPolar(self.QS_asic_index, 1, 0, 99, DACamplitude, DACoffset)
    return


def set_diffDAC(self,tension):
    client = self.connect_QubicStudio()
    if client==None:return None
    
    if tension > 0 and tension <= 3.5:
        diffDAC = tension / 2 / 7 * 65536 - 1
    else:
        diffDAC = 65536 * (1 + tension / 2 / 7)
    diffDAC = int(np.round(diffDAC))
    print('Setting diff DAC: ', diffDAC)
    client.sendSetDiffDAC(self.QS_asic_index, diffDAC)
    return



def set_slowDAC(self,tension):
    client = self.connect_QubicStudio()
    if client==None:return None
    
    if tension > 0 and tension <=3.5:
	slowDAC = tension / 1.4272e-4 - 1
    else:
	slowDAC = 65536 + tension / 1.4272e-4
        
    slowDAC = int(np.round(slowDAC))
    print('Setting slow DAC: ', slowDAC)
    client.sendSetSlowDAC(self.QS_asic_index, slowDAC)
    return



def get_iv_data(self,replay=False,TES=None,monitor=False):
    '''
    get IV data and make a running plot
    optionally, replay saved data.

    you can monitor the progress of a given TES by the keyword TES=<number>

    setting monitor=True will monitor *all* the TES, but this slows everything down
    enormously!  Not recommended!!

    '''

    monitor_iv=False
    if not TES==None:
        monitor_TES_index=self.TES_index(TES)
        monitor_iv=True

    if replay:
        if not isinstance(self.adu,np.ndarray):
            print('Please read an I-V data file, or run a new measurement!')
            return None
        if not isinstance(self.vbias,np.ndarray):
            print('There appears to be I-V data, but no Vbias info.')
            print('Please run make_Vbias() with the correct max and min values')
            return None
        vbias=self.vbias
        adu=self.adu
    else:
        client = self.connect_QubicStudio()
        if client==None: return None
        self.obsdate=dt.datetime.utcnow()
        if not isinstance(self.vbias,np.ndarray):
            vbias=make_Vbias()
        nbias=len(self.vbias)
        adu = np.empty((self.NPIXELS,nbias))

    vbias=self.vbias
    nbias=len(self.vbias)

    # figavg=self.setup_plot_Vavg()
    if monitor_iv:figiv,axiv=self.setup_plot_iv(TES)
    if monitor:
        nrows=16
        ncols=8
        figmulti,axmulti=self.setup_plot_iv_multi()
    
    for j in range(nbias) :
        self.debugmsg("Vbias=%gV " % vbias[j])
        if not replay:
            self.set_VoffsetTES(vbias[j],0.0)
            self.wait_a_bit()
            Vavg= self.get_mean()
            adu[:,j]=Vavg
            self.oxford_read_bath_temperature()
        else:
            Vavg=adu[:,j]

        # print ("a sample of V averages :  %g %g %g " %(Vavg[0], Vavg[43], Vavg[73]) )
        # plt.figure(figavg.number)
        # self.plot_Vavg(Vavg,vbias[j])
        if monitor_iv:
            plt.figure(figiv.number)
            I_tes=adu[monitor_TES_index,0:j+1]
            Iadjusted=self.ADU2I(I_tes)
            self.draw_iv(Iadjusted,axis=axiv)

        if monitor:
            # monitor all the I-V curves:  Warning!  Extremely slow!!!
            TES_index=0
            for row in range(nrows):
                for col in range(ncols):
                    axmulti[row,col].get_xaxis().set_visible(False)
                    axmulti[row,col].get_yaxis().set_visible(False)

                    Iadjusted=self.ADU2I(self.adu[TES_index,0:j+1])
                    self.draw_iv(Iadjusted,colour='blue',axis=axmulti[row,col])
                    text_y=min(Iadjusted)
                    axmulti[row,col].text(max(self.vbias),text_y,str('%i' % (TES_index+1)),va='bottom',ha='right',color='black')
            
                    TES_index+=1
        


    # plt.show()
    self.endobs=dt.datetime.utcnow()
    self.assign_ADU(adu)
    if not replay:
        self.write_fits()
    
    return adu
