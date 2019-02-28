#!/usr/bin/env python
'''
$Id: timestamping_diagnostic.py
$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
$created: Wed 27 Feb 2019 15:39:15 CET
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

make a diagnostic plot of the derived timestamps

'''
from matplotlib import pyplot as plt
import numpy as np


'''
# this script was originally tested on the following data:
a2=qp()
a2.read_qubicstudio_dataset('2019/2019-02-22/2019-02-22_16.28.01__Scan2/',asic=2)
pps = a2.hk['ASIC_SUMS']['PPS']
gps = a2.hk['ASIC_SUMS']['GPS']
tstamps    = a2.timeline_timeaxis(axistype='pps')
indextime  = a2.timeline_timeaxis(axistype='index')
compstamps = a2.timeline_timeaxis(axistype='computertime')
'''

def plot_timestamp_diagnostic(pps,gps,compstamps,indextime=None):

    ttl = 'Timestamps diagnostic'
    go=qp()
    npts = len(pps)
    pps_high = np.where(pps==1)[0]
    pps_indexes = []
    prev = gps[0]
    for idx in pps_high:
        if (idx>0 and pps[idx-1]==0) or (idx<npts-1 and pps[idx+1]==0):
            pps_indexes.append(idx)
            prev = gps[idx]            

    
    tstamps = go.pps2date(pps,gps)
    t0 = tstamps[0]

    if indextime is not None:
        slope = indextime[-1]/(len(tstamps)-1)
    else:
        slope = (tstamps[-1] - tstamps[0])/(len(tstamps)-1)
    offset = t0

    # subtract the progression to view only the residues (horizontal line)
    xpts = np.arange(len(tstamps))
    ypts = slope*xpts + offset

    plt.ion()
    fig1 = plt.figure(figsize=(16,8))
    fig1.canvas.set_window_title('plt: %s' % ttl)
    plt.title('timestamps')
    if indextime is not None:
        plt.plot(indextime+t0,                ls='none',marker='d',label='index time')
    plt.plot(tstamps,                         ls='none',marker='o',label='derived timestamps')
    plt.plot(compstamps,                      ls='none',marker='*',label='computer time')
    plt.plot(gps,                             ls='none',marker='x',label='GPS')
    plt.plot(pps_high,tstamps[pps_high],      ls='none',marker='^',label='pps high')
    plt.plot(pps_indexes,tstamps[pps_indexes],ls='none',marker='v',label='pps indexes')
    ax1 = fig1.axes[0]
    ax1.set_ylabel('seconds')
    ax1.set_ylim(compstamps.min(),compstamps.max())
    ax1.set_xlabel('sample number')
    plt.legend()
    pngname = '%s_full.png' % ttl.lower().replace(' ','_')
    plt.savefig(pngname,format='png',dpi=100,bbox_inches='tight')

    xwin0 = 300500
    xwin1 = 301500
    ax1.set_xlim(xwin0,xwin1)
    ax1.set_ylim(tstamps[xwin0],tstamps[xwin1])
    pngname = '%s_zoom.png' % ttl.lower().replace(' ','_')
    plt.savefig(pngname,format='png',dpi=100,bbox_inches='tight')

    # second plot: slope removed
    ttl = '%s horizontal' % ttl
    fig2 = plt.figure(figsize=(16,8))
    fig2.canvas.set_window_title('plt: %s' % ttl)
    plt.title('timestamps horizontal projection')
    if indextime is not None:
        plt.plot(indextime-ypts+t0,                ls='none',marker='d',label='index time')
    plt.plot(tstamps-ypts,                         ls='none',marker='o',label='derived timestamps')
    plt.plot(compstamps-ypts,                      ls='none',marker='*',label='computer time')
    plt.plot(gps-ypts,                             ls='none',marker='x',label='GPS')

    '''
    xpts = np.arange(len(pps_high))
    ypts = slope*xpts + offset    
    plt.plot(pps_high-ypts,tstamps[pps_high],      ls='none',marker='^',label='pps high')

    
    xpts = np.arange(len(pps_indexes))
    ypts = slope*xpts + offset    
    plt.plot(pps_indexes-ypts,tstamps[pps_indexes],ls='none',marker='v',label='pps indexes')
    '''
    ax2 = fig2.axes[0]
    ax2.set_ylabel('seconds')
    ax2.set_xlabel('sample number')
    horiz_y = tstamps - ypts
    #ax2.set_ylim(horiz_y.min(),horiz_y.max())
    ax2.set_ylim(-0.5,0.015)
    plt.legend()
    pngname = '%s_full.png' % ttl.lower().replace(' ','_')
    plt.savefig(pngname,format='png',dpi=100,bbox_inches='tight')

    ax2.set_ylim(-0.015,0.015)
    ax2.set_xlim(10500,13500)
    pngname = '%s_zoom.png' % ttl.lower().replace(' ','_')
    plt.savefig(pngname,format='png',dpi=100,bbox_inches='tight')
    
    return

