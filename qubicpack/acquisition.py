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


Note on the use of sendSetCalibPolar()
see comments by Pierre Chanial in dispatcheraccess.pyx
translated here...

sendSetCalibPolar(int asic, int mode, int shape, int frequency, int amplitude, int offset)

this sets the shape of the Bias Voltage.  
The French for "Bias Voltage" is "Polarisation", which is very confusing.
and then the word is further truncated to "Polar"

arguments:
  asic:  
       asic=0xFF : all ASIC's receive the command
       asic<16 : command sent to the specified ASIC
       asic bits 8 to 23 : send to a list of ASICs
                           example: 0x00FF00 corresponds to ASIC 0 to 7
                           example: 0x0AD200 corresponds to ASIC 0,3,6,9

  mode:
       mode=0 : no signal
       mode=1 : apply Bias voltage

  shape: 
       shape=0 : sinus
       shape=1 : triangle
       shape=2 : continuous

  frequency:
       frequency=99 defaults to lowest possible value.  i.e. f=1Hz


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

def verify_QS_connection(self):
    '''
    verify that we have a valid connection to QubicStudio
    This is useful for verifying that we're trying to connect to the correct ASIC
    '''
    client = self.connect_QubicStudio()
    if client==None:return False

    parameter = 'QUBIC_PixelScientificDataTimeLine_%i' % self.QS_asic_index
    req = client.request(parameter)

    try:
        timeline=req.next()
    except Exception as e:
        msg= '\n*****************************************************************************'
        msg+='\nERROR! Could not get data from QubicStudio.  Did you choose the correct ASIC?'
        msg+='\n       ASIC=%i' % self.asic
        msg+='\n       %s' % e
        msg+='\n*****************************************************************************\n'
        print(msg)
        return False

    return True
    

def configure_PID(self,P=0,I=20,D=0):
    '''
    configure the FLL (Flux Lock Loop) PID
    '''
    client = self.connect_QubicStudio()
    if client==None:return False

    # first switch off the loop
    client.sendActivatePID(self.QS_asic_index,0)

    # wait a bit
    self.wait_a_bit()

    # next, set the parameters
    client.sendConfigurePID(self.QS_asic_index, P,I,D)

    # wait a bit
    self.wait_a_bit()

    # and reactivate the loop
    client.sendActivatePID(self.QS_asic_index,1)

    # wait a bit before returning
    self.wait_a_bit()

    return True


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

    # reconfigure the FLL (stop/start)
    #if not self.configure_PID(0,20,0):return None ### this shouldn't go here.
        
    nsample = client.fetch('QUBIC_Nsample')
    # QubicStudio returns an array of integer of length 1.
    # convert this to a simple integer
    nsample = int(nsample)
    self.debugmsg('nsample=%i' % nsample)
    self.nsamples=nsample

    period = self.sample_period()
    self.debugmsg('period=%.3f msec' % (1000*period))
    self.debugmsg ('integration_time=%.2f' % self.tinteg)
    timeline_size = int(np.ceil(self.tinteg / period))
    self.debugmsg('timeline size=%i' % timeline_size)
    chunk_size = client.fetch('QUBIC_PixelScientificDataTimeLineSize')
    timeline = np.empty((self.NPIXELS, timeline_size))

    # date of the observation
    self.assign_obsdate()

    # bath temperature
    self.oxford_read_bath_temperature()
    
    parameter = 'QUBIC_PixelScientificDataTimeLine_%i' % self.QS_asic_index
    req = client.request(parameter)
    istart = 0
    for i in range(int(np.ceil(timeline_size / chunk_size))):
        delta = min(chunk_size, timeline_size - istart)
        timeline[:, istart:istart+delta] = req.next()[:, :delta]
        istart += chunk_size
    req.abort()
    return timeline    

def set_VoffsetTES(self, bias, amplitude, frequency=99, shape=0):
    '''
    command the bias voltage for the TES array
    integration time, asic, should be selected previously with the appropriate assign_() method
    ''' 
    client = self.connect_QubicStudio()
    if client==None:return None

    DACoffset=self.bias_offset2DAC(bias)
    DACamplitude=self.amplitude2DAC(amplitude)

    
    # arguments (see comments at top of file):
    #                                      asic, on/off, shape, frequency, amplitude,   offset
    self.bias_frequency=frequency
    client.sendSetCalibPolar(self.QS_asic_index, 1,      shape, frequency, DACamplitude, DACoffset)
    # wait and send the command again to make sure
    self.wait_a_bit()
    client.sendSetCalibPolar(self.QS_asic_index, 1, shape, frequency, DACamplitude, DACoffset)
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
    if isinstance(TES,int):
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
        self.assign_obsdate(dt.datetime.utcnow())
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

    # before starting, reset the FLL
    #if not replay: self.configure_PID() ### this is causing problems
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


def get_iv_timeline(self,vmin=None,vmax=None,frequency=None):
    '''
    get timeline data with Bias set to sinusoid shape and then extract the I-V data

    integration time should be set previously with assign_integration_time()
    if vmin,vmax are not given, try to get them from self.vbias
    '''

    if vmin==None:
        if not isinstance(self.vbias,np.ndarray):
            vbias=self.make_Vbias()
        vmin=min(self.vbias)
    if vmax==None:
        if not isinstance(self.vbias,np.ndarray):
            vbias=self.make_Vbias()
        vmax=max(self.vbias)

    self.min_bias=vmin
    self.max_bias=vmax
    
    amplitude=0.5*(vmax-vmin)
    offset=vmin+amplitude
    
    if frequency==None:frequency=99
    self.debugmsg('amplitude=%.2f, offset=%.2f, frequency=%.2f' % (amplitude,offset,frequency))
    ret=self.set_VoffsetTES(offset, amplitude, frequency=frequency, shape=0)

    timeline=self.integrate_scientific_data()
    if not isinstance(timeline,np.ndarray):
        print('ERROR! could not acquire timeline data')
        return None
        
    npts_timeline=timeline.shape[1]
    self.debugmsg('number of points in timeline: %i' % npts_timeline)


    # if this is the first one, assign a new timeline array
    if not self.exist_timeline_data(): self.timelines=[]
    self.timelines.append(timeline)
    return timeline
