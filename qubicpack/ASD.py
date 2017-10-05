"""
$Id: ASD.py
$auth: Michel Piat

$maintainer: Steve Torchinsky <satorchi@apc.in2p3.fr>
$created: Wed 05 Jul 2017 17:32:31 CEST
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

plot Amplitude Spectrum Density of time varying TES current
"""
from __future__ import division, print_function
import numpy as np
import pystudio
import sys,os,time
import datetime as dt
import matplotlib.pyplot as plt
from glob import glob
import matplotlib.mlab as mlab
import pickle

def plot_ASD(self,TES=1,tinteg=None,picklename=None,ntimelines=10,replay=False):
    '''
    get timeline data and plot the Amplitude Spectral Density
    timeline data is saved in FITS file, unless in monitor mode.
    in monitor mode, the plots will refresh indefinitely.  exit with Ctrl-C
    '''
    TES_index=self.TES_index(TES)
    monitor_mode=False
    if not isinstance(ntimelines,int) or ntimelines<=0:
        monitor_mode=True

        

    if isinstance(picklename,str) and os.path.exists(picklename):
        ''' 
        legacy: pickle file was only used once.  Use FITS from now on.        
        '''
        h=open(picklename,'r')
        timelines=pickle.load(h)
        self.timelines=timelines
        replay=True
        tinteg=10.
        ntimelines=timelines.shape[0]
        self.assign_obsdate(self.read_date_from_filename(picklename))
        self.nsamples=100 # this should be read from file!

    if replay:
        '''
        replay data that is imported from file.  This is for testing.
        '''
        if not isinstance(self.timelines,np.ndarray):
            print('Please read a timeline file, or run a new measurement!')
            return None
        ntimelines=self.timelines.shape[0]
        
    else:
        '''
        acquire new timeline data
        '''
        self.assign_integration_time(tinteg)  # s
        client=self.connect_QubicStudio()
        self.nsamples = client.fetch('QUBIC_Nsample')
        self.assign_obsdate()

    fs = 20000/self.NPIXELS*(100/self.nsamples)
    
    if not monitor_mode: saved_timelines=[]
    ttl='Timeline and Amplitude Spectral Density'
    subttl='\nASIC %i, TES #%i' % (self.asic,TES)
    
    nrows=1
    ncols=2
    plt.ion()
    fig,axes=plt.subplots(nrows,ncols,sharex=False,sharey=False,figsize=self.figsize)
    ax_timeline=axes[0]
    ax_asd=axes[1]
    fig.canvas.set_window_title('plt: '+ttl)
    fig.suptitle(ttl+subttl,fontsize=16)

    ax_asd.set_xlabel('freq')
    ax_asd.set_ylabel('P')

    ax_timeline.set_xlabel('time')
    ax_timeline.set_ylabel('A')
    
    filerootname=self.obsdate.strftime('AmplitudeSpectralDensity_%Y%m%dT%H%M%SUTC')
    txt_x=0.05
    txt_y=0.02
    idx=0
    while idx<ntimelines or monitor_mode:
        
	if not replay:
            timeline = self.integrate_scientific_data()
            if not monitor_mode: saved_timelines.append(timeline)
        else:
            timeline = self.timelines[idx,:,:]
            
        if not isinstance(timeline,np.ndarray):
            plt.close(fig)
            return None


        data_time=dt.datetime.utcnow()
        time_txt=data_time.strftime('%Y-%m-%m %H:%M:%S UTC')
        
	PSD, freqs = mlab.psd(timeline[TES_index],
                              Fs = fs,
                              NFFT = timeline.shape[1],
                              window=mlab.window_hanning,
                              detrend='mean')

        
        ax_timeline.cla()
	ax_timeline.plot(timeline[TES_index])
        ax_timeline.text(txt_x,txt_y,time_txt,transform=ax_timeline.transAxes)
        plt.pause(0.01)

        ASD=np.sqrt(PSD)
        ax_asd.cla()
	ax_asd.loglog(freqs,ASD)
        ax_asd.text(txt_x,txt_y,time_txt,transform=ax_asd.transAxes)
        plt.pause(0.01)
        
        if not monitor_mode:
            pngname=str('%s_TES%03i_timeline%03i.png' % (filerootname,TES,idx))
            plt.savefig(pngname,format='png',dpi=100,bbox_inches='tight')

        idx+=1

    plt.show()

    if not replay and not monitor_mode:
        self.timelines=np.array(saved_timelines)
        self.write_fits()

    return self.timelines

