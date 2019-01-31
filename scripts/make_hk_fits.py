#!/usr/bin/env python
'''
$Id: make_hk_fits.py
$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
$created: Thu 31 Jan 2019 17:27:33 CET
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

make a FITS file with all the housekeeping data recorded on qubic-central
the data are found in /home/qubic/data/temperature/broadcast
'''
from __future__ import division, print_function
import sys,os,re,time
import datetime as dt
from glob import glob
import numpy as np
from astropy.io import fits as pyfits

from qubicpack.hk.hk_file_tools import read_hk_file, read_entropy_label, read_entropy_logfile, read_temperature_dat

# a dictionary will have all the HK data
# the keys of the dictionary are the labels of each housekeeping item
# each dictionary entry will be a sub-dictionary with entries: value, time, unit
hk = {}

if 'HOME' in os.environ:
    homedir = os.environ['HOME']
else:
    homedir = '/home/qubic'


hk_topdir = '/home/qubic/data/temperature/broadcast'


# The Housekeeping types are the items saved by the housekeeping broadcast:
#   AVS47_1 (this is managed by the Entropy machine, and already read above)
#   AVS47_2 (this is managed by the Entropy machine, and already read above)
#   TEMPERATURE
#   MHS (Mechanical Heat Switch: also managed by the Entropy machine)
#   HEATER_Amp (powersupply current)
#   HEATER_Volt (powersupply voltage)
HKtypes = {}
HKtypes['AVS47_1'] = {}
HKtypes['AVS47_2'] = {}
HKtypes['TEMPERATURE'] = {}
HKtypes['MHS'] = {}
HKtypes['HEATER_Amp'] = {}
HKtypes['HEATER_Volt'] = {}
HKtypes['PRESSURE'] = {}

# set up the default labels for each housekeeping item
HKtypes['AVS47_1']['labels'] = ['Touch',
                                '1K stage',
                                'RIRT 300mK stage',
                                'M1',
                                'Cold head 1K',
                                'Film breaker',
                                'Cold head 300mK',
                                'M2']
HKtypes['AVS47_1']['unit'] = 'K'
HKtypes['AVS47_1']['nchannels'] = len(HKtypes['AVS47_1']['labels'])
HKtypes['AVS47_1']['fmtstr'] = 'AVS47_1_ch%i'

HKtypes['AVS47_2']['labels']= ['1K link',
                               'PT2 cold head',
                               'Fridge assemby right',
                               'Mech HS support',
                               'Fridge assembly left',
                               'AVS47_2 ch5',
                               'AVS47_2 ch6',
                               'AVS47_2 ch7']
HKtypes['AVS47_2']['unit'] = 'K'
HKtypes['AVS47_2']['nchannels'] = len(HKtypes['AVS47_2']['labels'])
HKtypes['AVS47_2']['fmtstr'] = 'AVS47_2_ch%i'


HKtypes['TEMPERATURE']['labels'] = ['40K filters',
                                    '40K sd',
                                    '40K sr',
                                    'PT2 s1',
                                    'PT1 s1',
                                    '4K filters',
                                    'HWP1',
                                    'HWP2',
                                    '4K sd',
                                    '4K PT2 CH',
                                    'PT1 s2',
                                    'PT2 s2',
                                    '300mK-4CP-D-1',
                                    '300mK-4HS-D-1',
                                    '300mK-3CP-D-1',
                                    '300mK-3HS-D-1',
                                    '1K-4HS-D-1',
                                    '1K-4CP-D-1']
HKtypes['TEMPERATURE']['unit'] = 'K'
HKtypes['TEMPERATURE']['nchannels'] = len(HKtypes['TEMPERATURE']['labels'])
HKtypes['TEMPERATURE']['fmtstr'] = 'TEMPERATURE%02i'

nMHS = 2
HKtypes['MHS']['labels'] = [ 'MHS%i' % (idx+1) for idx in range(nMHS) ]
HKtypes['MHS']['unit'] = 'steps'
HKtypes['MHS']['nchannels'] = len(HKtypes['MHS']['labels'])
HKtypes['MHS']['fmtstr'] = 'MHS%i'

nHEATER = 6
HKtypes['HEATER_Volt']['labels'] = [ 'HEATER%i_Volt' % (idx+1) for idx in range(nHEATER) ]
HKtypes['HEATER_Volt']['unit'] = 'V'
HKtypes['HEATER_Volt']['nchannels'] = len(HKtypes['HEATER_Volt']['labels'])
HKtypes['HEATER_Volt']['fmtstr'] = 'HEATER%i_Volt'

HKtypes['HEATER_Amp']['labels'] = [ 'HEATER%i_Amp' % (idx+1) for idx in range(nHEATER) ]
HKtypes['HEATER_Amp']['unit'] = 'mA'
HKtypes['HEATER_Amp']['nchannels'] = len(HKtypes['HEATER_Amp']['labels'])
HKtypes['HEATER_Amp']['fmtstr'] = 'HEATER%i_Amp'

HKtypes['PRESSURE']['labels'] = ['pressure']
HKtypes['PRESSURE']['unit'] = 'mBar'
HKtypes['PRESSURE']['nchannels'] = len(HKtypes['PRESSURE']['labels'])
HKtypes['PRESSURE']['fmtstr'] = 'PRESSURE%i'


HKname2label = {} # This is a translation from hkname to the physical label
for key in HKtypes.keys():
    if key.find('AVS47')==0:
        ch_offset = 0
    else:
        ch_offset =1
    for idx in range(HKtypes[key]['nchannels']):
        ch = idx + ch_offset
        hkname = HKtypes[key]['fmtstr'] % ch
        label = HKtypes[key]['labels'][idx]
        if label not in hk.keys():
            hk[label] = {}
            hk[label]['time'] = np.empty(0)
            hk[label]['value'] = np.empty(0)
        hk[label]['unit'] = HKtypes[key]['unit']
        HKname2label[hkname] = label

keys = HKname2label.keys()
keys.sort()
for hkname in keys:
    basename = hkname+'.txt'
    filename = '%s/%s' % (hk_topdir,basename)
    label = HKname2label[hkname]
    tstamps, val = read_hk_file(filename)
    if tstamps is None: continue
    tstamp_end = tstamps[-1]

    if label not in hk.keys():
        hk[label] = {}
        hk[label]['value'] = val
        hk[label]['time'] = tstamps
    else:
        #print('appending data for "%s" in file %s' % (label,filename))
        hk[label]['value'] = np.append(hk[label]['value'],val)
        hk[label]['time'] = np.append(hk[label]['time'],tstamps)


    npts=len(val)
    tot_npts=len(hk[label]['value'])        
    end_date=dt.datetime.fromtimestamp(tstamp_end).strftime('%Y-%m-%d %H:%M:%S')
    print('%s npts=%8i tot_npts=%8i %s' % (end_date,npts,tot_npts,filename))


    
# the files were read not necessarily in chronological order.  We have to resort
start_ctime = float(dt.datetime.utcnow().strftime('%s.%f'))
end_ctime = 0.0
for label in hk.keys():
    sorted_index = sorted(range(len(hk[label]['time'])), key=lambda i: hk[label]['time'][i])
    hk[label]['time'] = hk[label]['time'][sorted_index]
    hk[label]['value'] = hk[label]['value'][sorted_index]

    if len(hk[label]['time'])>0:
        if hk[label]['time'][0] < start_ctime:
            start_ctime = hk[label]['time'][0]

        if hk[label]['time'][-1] > end_ctime:
            end_ctime = hk[label]['time'][-1]
        

# write the fits file
start_date = dt.datetime.fromtimestamp(start_ctime)
end_date = dt.datetime.fromtimestamp(end_ctime)
datefmt = '%Y-%m-%d %H:%M:%S UTC'
start_date_str = start_date.strftime(datefmt)
end_date_str = end_date.strftime(datefmt)
fitsfile = 'QUBIC_HK_%s.fits' % start_date.strftime('%Y%m%d-%H%M%S')
prihdr = pyfits.Header()
prihdr['TELESCOP'] = ('QUBIC','Telescope used for the observation')
prihdr['OBSERVER'] = ('APC','name of the observer')
prihdr['AUTHOR'] = ('qubicpack by Steve Torchinsky https://github.com/satorchi/pystudio','')
prihdr['FILEDATE'] = (dt.datetime.utcnow().strftime(datefmt),'date this file was written')
prihdr['DATE-OBS'] = (start_date_str,'date of the observation in UTC')
prihdr['END-OBS']  = (end_date_str,'end time of the observation in UTC')
prihdr['N-HK'] = (len(hk),'number of housekeeping items')
prihdr.add_comment('each binary table has two columns corresponding to the date and values')
for idx,label in enumerate(hk.keys()):
    prikey = 'HK%02i' % (idx+1)
    prihdr[prikey] = (label,'label for FITS binary table %2i' % (idx+1))
prihdu = pyfits.PrimaryHDU(header=prihdr)


tbhdu = []
for label in hk.keys():

    dimstr = '%i' % len(hk[label]['value'])

    col1 = pyfits.Column(name='DATE', format='D', dim=dimstr, unit='seconds', array=hk[label]['time'])
    col2 = pyfits.Column(name=label, format='D', dim=dimstr, unit=hk[label]['unit'],  array=hk[label]['value'])
    cols  = pyfits.ColDefs([col1,col2])
    tbhdu.append(pyfits.BinTableHDU.from_columns(cols))


hdulist = pyfits.HDUList([prihdu]+tbhdu)
hdulist.writeto(fitsfile,overwrite=True)
