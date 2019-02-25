#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
$Id: tools.py
$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

tools which are generally useful for scripts using pystudio

"""
from __future__ import division, print_function
import numpy as np
import sys,os,time,subprocess,struct
import datetime as dt
from glob import glob
import pickle
from astropy.io import fits as pyfits


def read_date_from_filename(self,filename):
    '''
    read the date from the filename. 
    this hasn't been used in a long time
    '''
    try:
        datestr=filename.split('_')[-1].split('.')[0]
        date=dt.datetime.strptime(datestr,'%Y%m%dT%H%M%SUTC')
    except:
        date=None
    return date

def data_subdir(self):
    '''
    make a subdirectory for output files based on the date of the data acquisition
    '''
    if not isinstance(self.obsdate,dt.datetime):
        print('ERROR! No date for this data.')
        return None

    if not isinstance(self.datadir,str):
        datadir=self.assign_datadir()
        if datadir is None:return None

    subdir=self.obsdate.strftime('%Y/%Y%m%d')
    fullpath='%s%s%s' % (self.datadir,os.sep,subdir)
    # make the subdirectory if necessary
    if not os.path.exists(fullpath):
        cmd='mkdir -p %s' % fullpath
        proc=subprocess.Popen(cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out,err=proc.communicate()

    if not os.path.exists(fullpath):
        print('ERROR! Could not create subdirectory: %s' % fullpath)
        return None
    
    return subdir

def output_filename(self,rootname):
    '''
    assign a filename for plots, data, etc with the full path
    '''
    if not isinstance(rootname,str):
        return None

    if not isinstance(self.datadir,str):
        self.assign_datadir()

    if not isinstance(self.datadir,str):
        print('ERROR! no appropriate location for file save.')
        return None

    subdir=self.data_subdir()
    if isinstance(subdir,str):
        filename='%s%s%s%s%s' % (self.datadir,os.sep,subdir,os.sep,rootname)
    else:
        filename='%s%s%s' % (self.datadir,os.sep,rootname)

    return filename


def keyvals(self):
    '''
    assign the FITS keyword values for the primary header
    the keyword descriptions are done in assign_variables.py
    '''
    keyvals={}
    keyvals['TELESCOP']='QUBIC'
    keyvals['OBSERVER']=self.observer
    keyvals['DATE-OBS']=self.obsdate.strftime('%Y-%m-%d %H:%M:%S UTC')
    keyvals['END-OBS']=self.endobs.strftime('%Y-%m-%d %H:%M:%S UTC')
    keyvals['NSAMPLES']=self.nsamples
    keyvals['INT-TIME']=self.tinteg
    keyvals['NPIXELS'] =self.NPIXELS
    keyvals['NPIXSAMP']=self.NPIXELS_sampled
    keyvals['ASIC']    =self.asic
    keyvals['QUBIC-IP']=self.QubicStudio_ip
    keyvals['NCYCLES'] =self.nbiascycles
    keyvals['CYCBIAS'] =self.cycle_vbias
    keyvals['TES_TEMP']=self.temperature
    keyvals['BIAS_MOD']=self.bias_frequency
    keyvals['BIAS_MIN']=self.min_bias
    keyvals['BIAS_MAX']=self.max_bias
    keyvals['BIAS_FAC']=self.bias_factor
    keyvals['BIASMODE']=self.bias_mode
    keyvals['FLL_STAT']=self.FLL_state
    keyvals['FLL_P']   =self.FLL_P
    keyvals['FLL_I']   =self.FLL_I
    keyvals['FLL_D']   =self.FLL_D
    keyvals['DET_NAME']=self.detector_name
    keyvals['R_FEEDBK']=self.Rfeedback
    keyvals['CHUNK']=self.chunk_size
    return keyvals
    

def write_fits(self):
    '''
    write data to file
    it could be timeline data or I-V data, or both
    '''
    datefmt='%Y%m%dT%H%M%SUTC'
    if self.obsdate is None: self.assign_obsdate()
    datestr=self.obsdate.strftime(datefmt)

    if self.endobs is None:
        self.endobs=self.obsdate

    keyvals=self.keyvals()
    prihdr = pyfits.Header()
    for key in self.fitsblurbs.keys():
        prihdr[key]=(keyvals[key],self.fitsblurbs[key])
    prihdu = pyfits.PrimaryHDU(header=prihdr)

    tbhdu0=None
    if not self.rawmask is None:
        col  = pyfits.Column(name='RawMask',format='I', unit='bitmask', array=self.rawmask)
        cols  = pyfits.ColDefs([col])
        tbhdu0 = pyfits.BinTableHDU.from_columns(cols)
    
    if isinstance(self.adu,np.ndarray):
        fitsfile=str('QUBIC_TES_%s.fits' % datestr)
        fitsfile_fullpath=self.output_filename(fitsfile)
        if os.path.exists(fitsfile_fullpath):
            print('file already exists! %s' % fitsfile_fullpath)
            fitsfile=dt.datetime.utcnow().strftime('resaved-%Y%m%dT%H%M%SUTC__')+fitsfile
            fitsfile_fullpath=self.output_filename(fitsfile)
            print('instead, saving to file: %s' % fitsfile_fullpath)

        fmtstr=str('%iD' % self.adu.shape[1])
        dimstr=str('%i' % self.adu.shape[0])
        #print('format=',fmtstr)
        #print('dim=',dimstr)
        col1  = pyfits.Column(name='V_tes', format=fmtstr, dim=dimstr, unit='ADU', array=self.adu)
        cols  = pyfits.ColDefs([col1])
        tbhdu1 = pyfits.BinTableHDU.from_columns(cols)

        col2  = pyfits.Column(name='V_bias',format='D', unit='V', array=self.vbias)
        cols  = pyfits.ColDefs([col2])
        tbhdu2 = pyfits.BinTableHDU.from_columns(cols)

        if tbhdu0 is None:
            thdulist = pyfits.HDUList([prihdu, tbhdu1, tbhdu2])
        else:
            thdulist = pyfits.HDUList([prihdu, tbhdu0, tbhdu1, tbhdu2])
        thdulist.writeto(fitsfile_fullpath)
        print('FITS file written: %s' % fitsfile_fullpath)

    if self.exist_timeline_data():
        fitsfile=str('QUBIC_timeline_%s.fits' % datestr)
        fitsfile_fullpath=self.output_filename(fitsfile)
        if os.path.exists(fitsfile_fullpath):
            print('file already exists! %s' % fitsfile_fullpath)
            fitsfile=dt.datetime.utcnow().strftime('resaved-%Y%m%dT%H%M%SUTC__')+fitsfile
            fitsfile_fullpath=self.output_filename(fitsfile)
            print('instead, saving to file: %s' % fitsfile_fullpath)

        ntimelines=self.ntimelines()

        hdulist=[prihdu]
        if not tbhdu0 is None:hdulist.append(tbhdu0)
                    
        for timeline_index in range(ntimelines):
            timeline_array=self.tdata[timeline_index]['TIMELINE']
            fmtstr=str('%iD' % timeline_array.shape[1])
            dimstr=str('%i' % timeline_array.shape[0])
            col1  = pyfits.Column(name='timelines', format=fmtstr, dim=dimstr, unit='ADU', array=timeline_array)
            cols  = pyfits.ColDefs([col1])
            tbhdu = pyfits.BinTableHDU.from_columns(cols)
            for keyword in self.fitsblurbs.keys():
                if keyword in self.tdata[timeline_index].keys():
                    val=self.tdata[timeline_index][keyword]
                    if isinstance(val,dt.datetime):
                        tbhdu.header[keyword]=(val.strftime('%Y-%m-%d %H:%M:%S UTC'),self.fitsblurbs[keyword])
                    else:
                        tbhdu.header[keyword]=(val,self.fitsblurbs[keyword])
                
            hdulist.append(tbhdu)
            
        thdulist = pyfits.HDUList(hdulist)
        thdulist.writeto(fitsfile_fullpath)
        print('FITS file written: %s' % fitsfile_fullpath)

    return

def read_fits(self,filename):
    '''
    open a FITS file and determine whether it is QubicStudio or QubicPack
    '''
    if not isinstance(filename,str):
        print('ERROR! please enter a valid filename.')
        return None
    
    if not os.path.exists(filename):
        print('ERROR! file not found: %s' % filename)
        return None

    print('reading fits file: %s' % filename)
    hdulist=pyfits.open(filename)
    nhdu=len(hdulist)

    # check if it's a QUBIC file
    if nhdu>1\
       and ('TELESCOP' in hdulist[0].header.keys())\
       and (hdulist[0].header['TELESCOP'].strip()=='QUBIC'):
        print('Reading QubicPack file: %s' % filename)
        return self.read_qubicpack_fits(hdulist)

    # check if it's a QubicStudio file
    # QubicStudio FITS files always have at least 2 HDUs, with nothing in the primary header
    nogood_msg = 'Unrecognized FITS file!'
    if 'INSTRUME' not in hdulist[1].header.keys():
        print("'INSTRUME' keyword not found\n%s" % nogood_msg)
        return False
    if hdulist[1].header['INSTRUME'].strip() !=  'QUBIC':
        print('Instrument is not QUBIC\n%s' % nogood_msg)
        return False
    if 'EXTNAME' not in hdulist[1].header.keys():
        print("'EXTNAME' keyword not found\n%s" % nogood_msg)
        return False
    
    print('Reading QubicStudio FITS file: %s' % filename)
    return self.read_qubicstudio_fits(hdulist)
    return False

def read_fits_field(self,hdu,fieldname):
    '''
    check if a field exists, and if so read the data
    '''
    nfields = hdu.header['TFIELDS']
    fieldnames = []
    for field_idx in range(nfields):
        fieldno = field_idx+1
        fieldnames.append(hdu.header['TTYPE%i' % fieldno].strip())

    if fieldname in fieldnames:
        field_idx = fieldnames.index(fieldname)
        return hdu.data.field(field_idx)

    return None


def read_qubicstudio_dataset(self,datadir,asic=None):
    '''
    read a QubicStudio data set which consists of a number of FITS files in a directory
    '''
    if not os.path.isdir(datadir):
        print('Please enter a valid directory.')
        return None

    if asic is None:
        asic = 1
        print('If you would like to read data for a specific ASIC, please include the keyword asic=<N>')
    print('Reading data for ASIC %i' % asic)

    scidir = '%s/Sums' % datadir
    hkdir = '%s/Hks' % datadir
    subdir = {}
    subdir['science'] = 'Sums'
    subdir['asic'] = 'Hks'
    subdir['hkextern'] = 'Hks'
    subdir['raw'] = 'Raws'
    subdir['MMR'] = 'Hks'
    subdir['hkintern'] = 'Hks'
    
    pattern = {}
    pattern['science'] = '%s/%s/science-asic%i-*.fits' % (datadir,subdir['science'],asic)
    pattern['asic'] = '%s/%s/conf-asics-*.fits' % (datadir,subdir['asic'])
    pattern['hkextern'] = '%s/%s/hk-extern-*.fits' % (datadir,subdir['hkextern'])
    pattern['hkintern'] = '%s/%s/hk-intern-*.fits' % (datadir,subdir['hkextern'])

    # check for files, and read if found
    for filetype in pattern.keys():
        files = glob(pattern[filetype])
        if len(files)==0:
            print('No %s data found in directory: %s/%s' % (filetype,datadir,subdir[filetype]))
            continue

        filename = files[0]
    
        # we expect only one file of each type (per ASIC)
        if len(files)>1:
            print('WARNING! There are %i %s data files!' % (len(files),filetype))
            print('         There should only be 1 file.')

        
        chk = self.read_fits(filename)
        # try to guess the name of the detector array (P87, or whatever)
        self.guess_detector_name()
    
    return

def read_qubicstudio_fits(self,hdulist):
    '''
    read a QubicStudio FITS file
    the argument h is an hdulist after opening the FITS file
    and having confirmed that it really is a QubicStudio FITS file
    '''

    nhdu = len(hdulist)
    hdu = hdulist[1] # the primary header has nothing in it
    keys = hdu.header.keys()

    # what kind of QubicStudio file?
    QS_filetypes = ['ASIC_SUMS','CONF_ASIC1','EXTERN_HK','ASIC_RAW','INTERN_HK','QS_HK_IMacrt_MMR3']
    extname = hdu.header['EXTNAME'].strip()
    if extname not in QS_filetypes:
        print('ERROR! Unrecognized QubicStudio FITS file: %s' % extname)
        return None

    self.datafiletype = extname

    # dictionary for the return of timeline data
    if self.tdata is None:self.tdata = [{}]
    tdata = self.tdata[-1]
    if 'WARNING' not in tdata.keys():
        tdata['WARNING'] = []
    
    # get the timeline data from each detector
    if extname=='ASIC_SUMS':
        self.read_qubicstudio_science_fits(hdu)
        
    if extname=='CONF_ASIC1':
        self.read_qubicstudio_asic_fits(hdulist)

    if extname=='EXTERN_HK':
        self.read_qubicstudio_hkextern_fits(hdu)

    hdulist.close()
    return True

def read_qubicstudio_science_fits(self,hdu):
    '''
    read the science data
    The HDU passed here as the argument should already have been identified as the Science HDU
    '''
    tdata = self.tdata[-1]
        
    # check which ASIC
    asic = hdu.header['ASIC_NUM']
    if self.asic is None:
        self.asic = asic
    elif self.asic != asic:
        msg='ERROR! ASIC Id does not match: previous=%i, current=%i' % (self.asic, asic)
        tdata['WARNING'].append(msg)
        print(msg)
        self.asic = asic


    # read the science data
    npts = hdu.header['NAXIS2']
    adu = np.zeros((self.NPIXELS,npts))
    for pix_idx in range(self.NPIXELS):
        pix_no = pix_idx+1
        fieldname = 'pixel%i' % pix_no
        adu[pix_idx,:] = self.read_fits_field(hdu,fieldname)
    tdata['TIMELINE'] = adu

    # get number of samples per sum
    #################################################################
    # mail from Michel 20181221:
    ## nsample=100 est le nombre total de points par TES. Cela
    ## permet de remonter à la fréquence d'échantillonnage:
    ## fs=2E6/128/nsample
    ##
    ## NbSamplesPerSum=64 est le nombre de points
    ## utilisé pour obtenir le signal scientifique, après le
    ## masquage de certains des 100 points par TES. En fait, le
    ## signal scientifique est la somme des 64 points non masqué sur
    ## les 100 échantillons pris sur chaque TES.
    #################################################################
    nbsamplespersum_list  =  self.read_fits_field(hdu,'NbSamplesPerSum')
    tdata['NSAMSUM_LST'] = nbsamplespersum_list
    NbSamplesPerSum = nbsamplespersum_list[-1]
    tdata['NbSamplesPerSum'] = NbSamplesPerSum
    ## check if they're all the same
    difflist = np.unique(nbsamplespersum_list)
    if len(difflist)!=1:
        msg = 'WARNING! nsamples per sum changed during the measurement!'
        print(msg)
        tdata['WARNING'].append(msg)


    # get the time axis
    computertime_idx = 0
    gpstime_idx = 1
    ppstime_idx = 2
    dateobs = []
    timestamp = 1e-3*hdu.data.field(computertime_idx)
    for tstamp in timestamp:
        dateobs.append(dt.datetime.fromtimestamp(tstamp))
    tdata['DATE-OBS'] = dateobs
    tdata['BEG-OBS'] = dateobs[0]
    self.obsdate = tdata['BEG-OBS']
    tdata['END-OBS'] = dateobs[-1]

    tdata['GPS'] = 1e-3*hdu.data.field(gpstime_idx)
    tdata['PPS'] = hdu.data.field(ppstime_idx)
    
    return

def read_qubicstudio_asic_fits(self,hdulist):
    '''
    read the data giving the ASIC configuration
    The HDU passed here as the argument should already have been identified as the ASIC HDU

    we should read the science data first, and then read the corresponding ASIC table
    '''
    if self.asic is None:
        print('ERROR! Please read the science data first (asic is unknown)')
        return None
    
    tdata = self.tdata[-1]

    # check which ASIC
    hdu = hdulist[self.asic]
    asic = hdu.header['ASIC_NUM']
    if self.asic != asic:
        msg="ERROR! I'm reading the wrong ASIC table!  want %i, found %i" % (self.asic, asic)
        tdata['WARNING'].append(msg)
        print(msg)
            
    # get the time axis
    computertime_idx = 0
    gpstime_idx = 1
    dateobs = []
    timestamp = 1e-3*hdu.data.field(computertime_idx)
    npts = len(timestamp)
    for tstamp in timestamp:
        dateobs.append(dt.datetime.fromtimestamp(tstamp))
    tdata['ASICDATE'] = dateobs
    tdata['BEGASIC%i' % asic] = dateobs[0]
    tdata['ENDASIC%i' % asic] = dateobs[-1]

    # print some info
    datefmt = '%Y-%m-%d %H:%M:%S'
    print('There are %i housekeeping measurements in the period %s to %s'\
          % (npts,dateobs[0].strftime(datefmt),dateobs[-1].strftime(datefmt)))
    
    # get the Raw Mask
    rawmask_lst = self.read_fits_field(hdu,'Raw-mask')
    tdata['RAW-MASK_LST'] = rawmask_lst
    tdata['RAW-MASK'] = rawmask_lst[0]
    print('WARNING!  Assuming Raw-mask did not change during the measurement.')
    print("          You can check by looking at .tdata[0]['RAW-MASK_LST']")    
    self.rawmask = tdata['RAW-MASK']

    # get bias level (this is given directly in Volts.  No need to translate from DAC values)
    # TESAmplitude is in fact, peak-to-peak, so multiply by 0.5
    amplitude = 0.5*self.read_fits_field(hdu,'TESAmplitude')
    offset = self.read_fits_field(hdu,'TESOffset')

    ## check if they're all the same
    bias_min = offset-amplitude
    tdata['BIAS_MIN_LST']=bias_min
    difflist = np.unique(bias_min)
    if len(difflist)!=1:
        msg = 'WARNING! Minimum Bias changed during the measurement!'
        print(msg)
        tdata['WARNING'].append(msg)
    tdata['BIAS_MIN'] = min(bias_min)
    self.min_bias = tdata['BIAS_MIN']
    
    bias_max = offset+amplitude
    tdata['BIAS_MAX_LST']=bias_max
    difflist = np.unique(bias_max)
    if len(difflist)!=1:
        msg = 'WARNING! Maximum Bias changed during the measurement!'
        print(msg)
        tdata['WARNING'].append(msg)
    tdata['BIAS_MAX'] = max(bias_max)
    self.max_bias = tdata['BIAS_MAX']

    # get the number of samples
    nsamples_list = self.read_fits_field(hdu,'nsample')
    tdata['NSAM_LST'] = nsamples_list
    tdata['NSAMPLES'] = nsamples_list[-1]
    self.nsamples = tdata['NSAMPLES']
    difflist = np.unique(nsamples_list)
    if len(difflist)!=1:
        msg = 'WARNING! nsample changed during the measurement!'
        tdata['WARNING'].append(msg)

    return

def read_qubicstudio_hkextern_fits(self,hdu):
    '''
    read the housekeeping data
    '''
    tdata = self.tdata[-1]
    testemp = hdu.data.field(5)
    min_temp = testemp.min()
    max_temp = testemp.max()
    temperature = testemp.mean()
    print('TES temperatures varies between %.1fmK and %.1fmK during the measurement' % (1000*min_temp,1000*max_temp))
    print('Using TES temperature %.1fmK' % (1000*temperature))
    self.tdata[0]['TES_TEMP'] = temperature
    self.temperature = temperature


    # When I have time, I'll implement reading all the other stuff
    return

def read_qubicpack_fits(self,h):
    '''
    read a FITS file that was written by QubicPack
    argument h is an hdulist after opening a FITS file
    and confirming that it really is a QubicPack fits file
    '''

    self.datafiletype='QP_FITS'
    self.observer=h[0].header['OBSERVER']
    self.assign_obsdate(dt.datetime.strptime(h[0].header['DATE-OBS'],'%Y-%m-%d %H:%M:%S UTC'))
            
    self.nsamples=h[0].header['NSAMPLES']
    if self.nsamples=='': self.nsamples=100 # data from 12/13 July 2017
    self.tinteg=h[0].header['INT-TIME']
    self.NPIXELS=h[0].header['NPIXELS']
    self.asic=h[0].header['ASIC']
    self.QubicStudio_ip=h[0].header['QUBIC-IP']

    if 'NCYCLES' in h[0].header.keys():
        self.debugmsg('reading ncycles')
        self.nbiascycles=h[0].header['NCYCLES']

    if 'CYCBIAS' in h[0].header.keys():
        self.debugmsg('reading cycle_vbias')
        self.debugmsg(str(h[0].header.cards[13]))
        self.cycle_vbias=h[0].header['CYCBIAS']
        self.debugmsg('cycle_vbias is %s' % str(self.cycle_vbias))

    if 'TES_TEMP' in h[0].header.keys():
        self.temperature=h[0].header['TES_TEMP']
    else:
        self.temperature=None

    if 'END-OBS' in h[0].header.keys():
        self.endobs=dt.datetime.strptime(h[0].header['END-OBS'],'%Y-%m-%d %H:%M:%S UTC')
    else:
        self.endobs=None

    if 'BIAS_MOD' in h[0].header.keys():
        self.bias_frequency=h[0].header['BIAS_MOD']
    if 'BIASMODE' in h[0].header.keys():
        self.bias_mode=h[0].header['BIASMODE']
    if 'BIAS_MIN' in h[0].header.keys():
        self.min_bias=h[0].header['BIAS_MIN']
    if 'BIAS_MAX' in h[0].header.keys():
        self.max_bias=h[0].header['BIAS_MAX']
    if 'BIAS_FAC' in h[0].header.keys():
        self.bias_factor=h[0].header['BIAS_FAC']

    if 'DET_NAME' in h[0].header.keys():
        self.detector_name=h[0].header['DET_NAME']
    # in case detector name is undefined...
    self.guess_detector_name()

    if 'R_FEEDBK' in h[0].header.keys():
        self.Rfeedback=h[0].header['R_FEEDBK']

    if 'FLL_STAT' in h[0].header.keys():
        self.FLL_state=h[0].header['FLL_STAT']
    if 'FLL_P' in h[0].header.keys():
        self.FLL_P=h[0].header['FLL_P']
    if 'FLL_I' in h[0].header.keys():
        self.FLL_I=h[0].header['FLL_I']
    if 'FLL_D' in h[0].header.keys():
        self.FLL_D=h[0].header['FLL_D']
                
    if 'NPIXSAMP' in h[0].header.keys():
        self.NPIXELS_sampled=h[0].header['NPIXSAMP']
    
    self.debugmsg('Finished reading the primary header.')
    
    self.tdata=[]
    for hdu in h[1:]:
        hdrtype=hdu.header['TTYPE1']

        if hdrtype=='RawMask':
            '''
            this is the mask of the samples (filtered out samples)
            '''
            self.debugmsg('Reading RawMask HDU')

            # number of values should be 125
            nvals=hdu.header['NAXIS2']
            self.debugmsg('RawMask: nvals=%i' % nvals)
            if nvals!=125:
                print('WARNING! RawMask has the wrong number of mask values: %i' % nvals)

            # read the raw mask
            self.rawmask=np.zeros(nvals,dtype=int)
            data=hdu.data
            for idx in range(nvals):
                self.rawmask[idx]=data[idx][0]
            self.debugmsg('Finished reading RawMask HDU')

                        
        if hdrtype=='V_tes':
            '''
            this is I-V data
            '''
        
            # number of bias points
            nbias=eval(hdu.header['TFORM1'].strip()[:-1])

            # read the adu matrix
            data=hdu.data
            self.adu=np.empty((self.NPIXELS,nbias))
            for n in range(self.NPIXELS):
                self.adu[n,:]=data[n][0]

        if hdrtype=='V_bias':
            '''
            this is the bias points
            '''

            data=hdu.data
            self.vbias=np.empty(nbias)
            for n in range(nbias):
                self.vbias[n]=data[n][0]
            self.max_bias=max(self.vbias)
            self.min_bias=min(self.vbias)
            self.max_bias_position=np.argmax(self.vbias)
            

        if hdrtype=='timelines':
            '''
            this is the timeline data
            '''
            print('reading timeline data')
            tdata={}
            data=hdu.data
            npts=eval(hdu.header['TFORM1'].strip()[:-1])
            timeline=np.empty((self.NPIXELS,npts))
            for n in range(self.NPIXELS):
                timeline[n,:]=data[n][0]
            tdata['TIMELINE']=timeline
            for keyword in self.fitsblurbs.keys():
                if keyword in hdu.header.keys():
                    if keyword=='DATE-OBS' or keyword=='END-OBS':
                        val=dt.datetime.strptime(hdu.header[keyword],'%Y-%m-%d %H:%M:%S UTC')
                    else:
                        val=hdu.header[keyword]
                    if val=='':val=None
                    tdata[keyword]=val

            self.tdata.append(tdata)

    h.close()


    if self.exist_iv_data():
        f=self.read_filter()
        if f is None:f=self.filter_iv_all()

    return


def read_bins(self,filename):
    if not isinstance(filename,str):
        print('ERROR! please enter a valid filename.')
        return None
            
    if not os.path.exists(filename):
        print('ERROR! file not found: %s' % filename)
        return None
            
    print('reading binary file: %s, I suppose this is a timeline' % filename)

    data=[]
    with open(filename, "rb") as f:
        b = f.read(14)
        data.append(struct.unpack('128i', f.read(4*128)))
        while f.read(14) != "": data.append(struct.unpack('128i', f.read(4*128)))
        
    data=np.asarray(zip(*data))
    self.NPIXELS=128
    npts=int(data.size/128.)

    timeline_array=[]
    timeline_tes=np.empty((npts))
    for n in range(self.NPIXELS):
        timeline_tes=data[n]        
        timeline_array.append(timeline_tes)

    timeline_array=np.array(timeline_array)
    self.tdata=[]
    tdata={}
    tdata['TIMELINE']=timeline_array
    self.tdata.append(tdata)
    f.close()
    return
        
def get_from_keyboard(self,msg,default=None):
    ''''
    get interactive input from the keyboard
    '''
    prompt='%s (default: %s) ' % (msg,str(default))
    ans=raw_input(prompt)
    if ans=='':return default
    if type(default)==str:
        return ans
    
    try:
        x=eval(ans)
    except:
        print('invalid response.')
        return None
    return x
    

def writelog(self,msg):
    '''
    write some output with a timestamp to a log file
    and also write it on the screen
    '''

    if self.logfile is None: self.assign_logfile()
    
    handle=open(self.logfile,'a')
    timestamp=dt.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC -- ')
    handle.write(timestamp+msg+'\n')
    handle.close()
    print(timestamp+msg)

    # send it to the QubicStudio logbook, if possible
    client=self.connect_QubicStudio(silent=True)
    if not client is None:client.sendAddToLogbook('pyStudio',msg)

    return
         

def pps2date(self,pps,gps):
    '''
    convert the gps date to a precise date given the pps
    '''
    npts = len(pps)

    pps_indexes = np.where(pps==1)[0]
    gps_indexes = []
    # there is exactly one second between gps_indexes
    # and the date is the one found at each gps_index
    tstamp = -np.ones(npts)
    last_one_is_no_good = False
    for idx in pps_indexes:
        gps_at_pps = gps[idx]
        next_gps = gps_at_pps
        offset_idx = idx
        while next_gps==gps_at_pps:
            offset_idx += 1
            if offset_idx>=npts:
                last_one_is_no_good = True
                break
            next_gps = gps[offset_idx]
            if not last_one_is_no_good:
                gps_indexes.append(offset_idx)

        tstamp[idx] = next_gps

    first_sample_period = None    
    for idx in range(len(pps_indexes)-1):
        diff_idx = pps_indexes[idx+1] - pps_indexes[idx]
        sample_period = 1.0/diff_idx # exactly one second between pulses
        if first_sample_period is None:
            first_sample_period = sample_period
        for idx_offset in range(diff_idx):
            tstamp[pps_indexes[idx]+idx_offset] = tstamp[pps_indexes[idx]] + idx_offset*sample_period

    last_sample_period = sample_period

    # do the first bit before the first PPS
    tstamp0 = tstamp[pps_indexes[0]]
    for idx in range(pps_indexes[0]+1):
        tstamp[pps_indexes[0] - idx] = tstamp0 - idx*first_sample_period

    # do the last bit after the last PPS
    tstampF = tstamp[pps_indexes[-1]]
    for idx in range(npts - pps_indexes[-1]):
        tstamp[pps_indexes[-1] + idx] = tstampF + idx*last_sample_period

    return tstamp
