#!/usr/bin/env python
'''
$Id: overnight_fast_iv.py
$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
$created: Tue 31 Oct 2017 16:42:05 CET
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

wrapper script to run several I-V measurements, changing the bath temperature for each one
we use the "fast I-V" method with the Bias modulated by a sine curve
'''
from __future__ import division, print_function
from qubicpack import qubicpack as qp
import matplotlib.pyplot as plt
import datetime as dt
import subprocess,os,sys,time
import numpy as np
reload(sys)
sys.setdefaultencoding('utf8')
from satorchipy.datefunctions import *

# set TESTMODE to False for a real measurement (default)
TESTMODE=False
if len(sys.argv)>1:
    if sys.argv[1].upper()=='--TESTMODE':
        TESTMODE=True

# precision required for bath temperature
temp_precision=0.005 # in Kelvin

# timeout for waiting for temperature to settle
if TESTMODE:
    temp_minwait=dt.timedelta(seconds=30)
    temp_timeout=dt.timedelta(seconds=60)
    temp_wait=dt.timedelta(seconds=1)
    wait_msg='waiting %.0f seconds for temperature to settle' % tot_seconds(temp_wait)
else:
    temp_minwait=dt.timedelta(minutes=30)
    temp_minwait=dt.timedelta(minutes=5)
    temp_timeout=dt.timedelta(minutes=60)
    temp_wait=dt.timedelta(minutes=1)
    wait_msg='waiting %.1f minutes for temperature to settle' % (tot_seconds(temp_wait)/60.)


    
def get_from_keyboard(msg,default=None):
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
    

def writelog(filename,msg):
    '''
    write some output with a timestamp to a log file
    and also write it on the screen
    '''
    handle=open(filename,'a')
    timestamp=dt.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC -- ')
    handle.write(timestamp+msg+'\n')
    handle.close()
    print(timestamp+msg)
    return

def read_bath_temperature(qpobject,logfile):
    Tbath=qpobject.oxford_read_bath_temperature()
    if Tbath==None:
        writelog(logfile,'ERROR! Could not read bath temperature.')
        Tbath=qpobject.temperature
    return Tbath

go=qp()
figsize=go.figsize
go.assign_integration_time(240.0)
# set debuglevel to 1 if you want lots of messages on the screen
go.debuglevel=1


'''
get parameters
'''

# can I get ASIC from QubicStudio?
asic=get_from_keyboard('Which ASIC?  ',2)
if asic==None:quit()
ret=go.assign_asic(asic)

# verify that we can get stuff from QubicStudio
ret=go.verify_QS_connection()
if not ret:quit()

# setup bias voltage range
min_bias=get_from_keyboard('minimum bias voltage ',0.5)
if min_bias==None:quit()
max_bias=get_from_keyboard('maximum bias voltage ',3.0)
if max_bias==None:quit()

# setup temperature range
start_temp=get_from_keyboard('start bath temperature ',0.6)
if start_temp==None:quit()
end_temp=get_from_keyboard('end bath temperature ',0.3)
if end_temp==None:quit()
step_temp=get_from_keyboard('temperature steps',0.025)
if step_temp==None:quit()

# make sure steps are negative if we're going down in temperature
if start_temp>end_temp:
    if step_temp>0:step_temp=-step_temp
else:
    if step_temp<0:step_temp=-step_temp

Tbath_target=np.arange(start_temp,end_temp,step_temp)

# if running in test mode, use a random generated result
if TESTMODE:
    go.adu=np.random.rand(go.NPIXELS,len(go.vbias))
    go.temperature=0.3
    go.nsamples=100
    go.OxfordInstruments_ip='127.0.0.1'

monitor_TES=get_from_keyboard('which TES would you like to monitor during the measurement? ',82)
if monitor_TES==None:quit()

# make a log file
logfile=dt.datetime.utcnow().strftime('temperature_IV_logfile_%Y%m%dT%H%M%SUTC.txt')
logfile_fullpath=go.output_filename(logfile)

writelog(logfile_fullpath,'starting I-V measurements at different temperatures using the timeline (fast) method')
writelog(logfile_fullpath,'ASIC=%i' % go.asic)
writelog(logfile_fullpath,'minimum bias=%.2f V' % min_bias)
writelog(logfile_fullpath,'maximum bias=%.2f V' % max_bias)
writelog(logfile_fullpath,'start temperature=%.3f K' % start_temp)
writelog(logfile_fullpath,'end temperature=%.3f K' % end_temp)
writelog(logfile_fullpath,'temperature step=%.3f K' % step_temp)
nsteps=len(Tbath_target)
writelog(logfile_fullpath,'number of temperatures=%i' % nsteps)

# estimated time: half hour for temperature to settle, 4 minutes for I-V measurement
duration_estimate=nsteps*(temp_minwait+dt.timedelta(minutes=4))
endtime_estimate=dt.datetime.utcnow()+duration_estimate
writelog(logfile_fullpath,endtime_estimate.strftime('estimated end at %Y-%m-%d %H:%M:%S'))

# run the measurement
for T in Tbath_target:
    # set the desired bath temperature
    cmdret=go.oxford_set_point(T)
    # make sure the set point was accepted
    Tsetpt=go.oxford_read_set_point()
    if Tsetpt==None:
        writelog(logfile_fullpath,'ERROR! Could not read set point temperature.')
        Tsetpt=T
    writelog(logfile_fullpath,'Temperature set point = %.2f mK' % (1000*Tsetpt))
    Tbath=read_bath_temperature(go,logfile_fullpath)
    Tbath_previous=Tbath
    delta=np.abs(Tbath - T)
    delta_step=np.abs(Tbath - Tbath_previous)
    start_waiting=dt.datetime.utcnow()
    end_waiting=start_waiting+temp_timeout
    min_endtime=start_waiting+temp_minwait
    
    while (delta>temp_precision
          or delta_step>temp_precision\
          or dt.datetime.utcnow()<min_endtime)\
          and dt.datetime.utcnow()<end_waiting:

        writelog(logfile_fullpath,wait_msg)
        time.sleep(tot_seconds(temp_wait))
        writelog(logfile_fullpath,'reading temperature')
        Tbath=read_bath_temperature(go,logfile_fullpath)
        delta_step=np.abs(Tbath - Tbath_previous)
        Tbath_previous=Tbath
        delta=np.abs(Tbath - T)
        writelog(logfile_fullpath,'Tbath=%0.2f mK' %  (1000*go.temperature))

        # check heater percentage
        heatpercent=go.oxford_read_heater_level()
        if heatpercent>99:
            writelog(logfile_fullpath,'We need to increase the maximum current to the heater')
            cmdret=go.oxford_increase_heater_range()
            heater=go.oxford_read_heater_range()
            writelog(logfile_fullpath,'heater range: %f mA' % heater)
        
    writelog(logfile_fullpath,'starting I-V measurement')
    if delta>temp_precision:
        writelog(logfile_fullpath,'WARNING! Did not reach target temperature!')
        writelog(logfile_fullpath,'Tbath=%0.2f mK, Tsetpoint=%0.2f mK' % (1000*Tbath,1000*T))

    # reset FLL before measurement
    if not TESTMODE:
        go.configure_PID()
        go.get_iv_timeline(vmin=min_bias,vmax=max_bias)
        go.timeline2adu(monitor_TES)
        go.write_fits()
    writelog(logfile_fullpath,'end I-V measurement')
    plt.close('all')

    # generate the test document
    writelog(logfile_fullpath,'generating test document')
    if not TESTMODE: pdfname=go.make_iv_report()
    writelog(logfile_fullpath,'test document generated')

    # reset the plotting figure size
    go.figsize=figsize

    # reset data
    if not TESTMODE:go.adu=None



# finally, switch off the temperature control loop
go.oxford_pidoff()

