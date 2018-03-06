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
import matplotlib.pyplot as plt
from glob import glob
import pickle
from astropy.io import fits as pyfits


def read_date_from_filename(self,filename):
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
        if datadir==None:return None

    subdir=self.obsdate.strftime('%Y/%Y%m%d')
    fullpath='%s%s%s' % (self.datadir,os.sep,subdir)
    # make the subdirectory if necessary
    if not os.path.exists(fullpath):
        cmd='mkdir --parents %s' % fullpath
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
    return keyvals
    

def write_fits(self):
    '''
    write data to file
    it could be timeline data or I-V data, or both
    '''
    datefmt='%Y%m%dT%H%M%SUTC'
    if self.obsdate==None: self.assign_obsdate()
    datestr=self.obsdate.strftime(datefmt)

    if self.endobs==None:
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
        if f==None:f=self.filter_iv_all()

    return


def read_bins(self,filename):
    if not isinstance(filename,str):
        print('ERROR! please enter a valid filename.')
        return None
            
    if not os.path.exists(filename):
        print('ERROR! file not found: %s' % filename)
        return None
            
    print('reading binary file: %s, I suppose this is a timeline' % filename)

    self.tdata=[]
    data=[]
    with open(filename, "rb") as f:
        b = f.read(14)
        data.append(struct.unpack('128i', f.read(4*128)))
        while f.read(14) != "": data.append(struct.unpack('128i', f.read(4*128)))
        
    data=np.asarray(zip(*data))
    self.NPIXELS=128
    npts=data.size/128.

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
         
