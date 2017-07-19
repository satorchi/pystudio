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

def plot_ASD(self,chan=0,tinteg=None,picklename=None,ntimelines=10,replay=False):

    # legacy: pickle file was only used once.  Use FITS from now on.
    if isinstance(picklename,str) and os.path.exists(picklename):
        h=open(picklename,'r')
        timelines=pickle.load(h)
        self.timelines=timelines
        replay=True
        tinteg=10.
        ntimelines=timelines.shape[0]
        self.obsdate=self.read_date_from_filename(picklename)
        if self.obsdate==None: self.obsdate=dt.datetime.utcnow()
        self.nsamples=100 # this should be read from file!
        

    self.assign_integration_time(tinteg)  # s
    tinteg=self.tinteg
    
    if not replay:
        client=self.connect_QubicStudio()
        self.nsamples = client.fetch('QUBIC_Nsample')
        self.obsdate=dt.datetime.utcnow()

    Ndet = self.NPIXELS
    fs = 20000/Ndet*(100/self.nsamples)
    
    saved_timelines=[]
    ttl=str('Timeline and Amplitude Spectral Density')
    plt.ion()

    nrows=1
    ncols=2
    plt.ion()
    fig,axes=plt.subplots(nrows,ncols,sharex=False,sharey=False,figsize=self.figsize)
    ax_timeline=axes[0]
    ax_asd=axes[1]
    fig.canvas.set_window_title('plt: '+ttl)
    fig.suptitle(ttl,fontsize=16)

    ax_asd.set_xlabel('freq')
    ax_asd.set_ylabel('P')

    ax_timeline.set_xlabel('time')
    ax_timeline.set_ylabel('A')
    
    filerootname=self.obsdate.strftime('AmplitudeSpectralDensity_%Y%m%dT%H%M%SUTC')
    for i in range(ntimelines):
	#print(i)
	if not replay:
            timeline = self.integrate_scientific_data()
            saved_timelines.append(timeline)
        else:
            timeline = timelines[i,:,:]
            
        if timeline==None:
            plt.close(fig)
            return None

        ax_timeline.cla()
	ax_timeline.plot(timeline[chan])
        plt.pause(0.01)
        
	PSD, freqs = mlab.psd(timeline[chan],
                              Fs = fs,
                              NFFT = timeline.shape[1],
                              window=mlab.window_hanning,
                              detrend='mean')

        
        ax_asd.cla()
	ax_asd.loglog(freqs,np.sqrt(PSD))
        plt.pause(0.01)
        pngname=str('%s_%03i.png' % (filerootname,i))
        plt.savefig(pngname,format='png',dpi=100,bbox_inches='tight')
            

    plt.show()

    # legacy:  Pickle file was used only once.  Now use FITS
    '''
    if not replay:
        opicklename=filerootname+'.pickle'
        timelines=np.array(saved_timelines)
        h=open(opicklename,'w')
        pickle.dump(timelines,h)
        h.close()
    '''
    if not replay:
        self.write_fits()

    return timelines

