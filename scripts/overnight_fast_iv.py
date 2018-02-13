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
import os
if 'SSH_CLIENT' in os.environ.keys():
    import matplotlib
    matplotlib.use('Agg')
from qubicpack import qubicpack as qp
import matplotlib.pyplot as plt
import datetime as dt
import subprocess,os,sys,time
import numpy as np
reload(sys)
sys.setdefaultencoding('utf8')
from satorchipy.datefunctions import *

def read_bath_temperature(qpobject,logfile):
    Tbath=qpobject.oxford_read_bath_temperature()
    if Tbath==None:
        qpobject.writelog(logfile,'ERROR! Could not read bath temperature.')
        Tbath=qpobject.temperature
    return Tbath

# create the  qubicpack object
go=qp()
figsize=go.figsize
# set debuglevel to 1 if you want lots of messages on the screen
go.debuglevel=1

# set TESTMODE to False for a real measurement (default)
TESTMODE=False

# default is to ask for parameters
# command line arguments will suppress questions for the corresponding parameters
asic=None
detname=None
meastype=None
timeline_period=240.0 # int time 4 minutes for I-V from timeline
frequency=99

# Mon 22 Jan 2018 08:46:16 CET: we have removed the 5x bias factor
go.max_permitted_bias=10.0
min_bias=None
max_possible_bias=go.DAC2V * 2**15
max_bias=None

start_temp=None
end_temp=None
step_temp=None

monitor_TES=None
monitor_TES_default=34

PID_I=None

argv=[]
if len(sys.argv)>1:argv=sys.argv[1:]
for arg in argv:
    if arg.upper()=='--TESTMODE':
        TESTMODE=True
        continue

    if arg.upper().find('--ASIC=')==0:
        asic=int(eval(arg.split('=')[1]))
        continue

    if arg.upper().find('--ARRAY=')==0:
        detname=arg.split('=')[1]
        continue

    if arg.upper().find('--MEASTYPE=')==0:
        meastype=arg.split('=')[1]
        continue

    if arg.upper().find('--MIN_BIAS=')==0:
        min_bias=eval(arg.split('=')[1])
        continue
    
    if arg.upper().find('--MAX_BIAS=')==0:
        max_bias=eval(arg.split('=')[1])
        continue

    if arg.upper().find('--START_TEMP=')==0:
        start_temp=eval(arg.split('=')[1])
        continue
    
    if arg.upper().find('--END_TEMP=')==0:
        end_temp=eval(arg.split('=')[1])
        continue

    if arg.upper().find('--STEP_TEMP=')==0:
        step_temp=eval(arg.split('=')[1])
        continue

    if arg.upper().find('--MONITOR_TES=')==0:
        monitor_TES=int(eval(arg.split('=')[1]))
        continue
    
# precision required for bath temperature
temp_precision=0.005 # in Kelvin

# timeout for waiting for temperature to settle
if TESTMODE:
    temp_minwait=dt.timedelta(seconds=30)
    temp_timeout=dt.timedelta(seconds=60)
    temp_wait=dt.timedelta(seconds=1)
    wait_msg='waiting %.0f seconds for temperature to settle' % tot_seconds(temp_wait)
else:
    temp_minwait=dt.timedelta(minutes=0.5)
    temp_timeout=dt.timedelta(minutes=5)
    temp_wait=dt.timedelta(minutes=0.25)
    wait_msg='waiting %.2f minutes for temperature to settle' % (tot_seconds(temp_wait)/60.)


    



'''
get parameters
'''

if meastype is None:
    meastype=go.get_from_keyboard('Which type of measurement (IV or RT)? ','IV')

meastype=meastype.upper()    
if not meastype=='RT':
    print('Doing I-V measurements.')
    timeline_period=240.0
    frequency=99
    PID_I=20
else:
    print('Doing R-T measurements.')
    timeline_period=60.0
    frequency=10.0
    min_bias=-0.5
    max_bias= 0.5
    PID_I=50
    
if detname is None:
    detname=go.get_from_keyboard('Which array is it? ','P90')
go.assign_detector_name(detname)

# can I get ASIC from QubicStudio?
if asic is None:
    asic=go.get_from_keyboard('Which ASIC?  ',2)
    if asic is None:quit()
ret=go.assign_asic(asic)

# setup bias voltage range
if min_bias is None:
    min_bias=go.get_from_keyboard('minimum bias voltage ',3.5)
    if min_bias==None:quit()

if max_bias is None:
    max_bias=go.get_from_keyboard('maximum bias voltage ',max_possible_bias)
    if max_bias==None:quit()

# setup temperature range
if start_temp is None:
    start_temp=go.get_from_keyboard('start bath temperature ',0.6)
    if start_temp==None:quit()
if end_temp is None:    
    end_temp=go.get_from_keyboard('end bath temperature ',0.3)
    if end_temp==None:quit()
if step_temp is None:
    step_temp_default=(end_temp-start_temp)/8.
    step_temp=go.get_from_keyboard('temperature steps',step_temp_default)
    if step_temp==None:quit()

# make sure steps are negative if we're going down in temperature
if start_temp>end_temp:
    if step_temp>0:step_temp=-step_temp
else:
    if step_temp<0:step_temp=-step_temp

Tbath_target=np.arange(start_temp,end_temp,step_temp)

if monitor_TES is None:    
    monitor_TES=go.get_from_keyboard('which TES would you like to monitor during the measurement? ',monitor_TES_default)
    if monitor_TES==None:quit()

# if running in test mode, use a random generated result
if TESTMODE:
    #go.adu=np.random.rand(go.NPIXELS,len(go.vbias))
    go.temperature=0.3
    go.nsamples=100
    go.OxfordInstruments_ip='127.0.0.1'
else:
    ret=go.verify_QS_connection()
    if not ret:quit()

# make a log file
logfile=dt.datetime.utcnow().strftime('temperature_IV_logfile_%Y%m%dT%H%M%SUTC.txt')
logfile_fullpath=go.output_filename(logfile)

go.writelog(logfile_fullpath,'starting I-V measurements at different temperatures using the timeline (fast) method')
go.writelog(logfile_fullpath,'ASIC=%i' % go.asic)
go.writelog(logfile_fullpath,'minimum bias=%.2f V' % min_bias)
go.writelog(logfile_fullpath,'maximum bias=%.2f V' % max_bias)
go.writelog(logfile_fullpath,'start temperature=%.3f K' % start_temp)
go.writelog(logfile_fullpath,'end temperature=%.3f K' % end_temp)
go.writelog(logfile_fullpath,'temperature step=%.3f K' % step_temp)
nsteps=len(Tbath_target)
go.writelog(logfile_fullpath,'number of temperatures=%i' % nsteps)

# estimated time: temperature settle time plus measurement time for I-V
duration_estimate=nsteps*(temp_minwait+dt.timedelta(seconds=timeline_period))
endtime_estimate=dt.datetime.utcnow()+duration_estimate
go.writelog(logfile_fullpath,endtime_estimate.strftime('estimated end at %Y-%m-%d %H:%M:%S'))

# run the measurement
for T in Tbath_target:
    # set the desired bath temperature
    cmdret=go.oxford_set_point(T)
    # make sure the set point was accepted
    Tsetpt=go.oxford_read_set_point()
    if Tsetpt==None:
        go.writelog(logfile_fullpath,'ERROR! Could not read set point temperature.')
        Tsetpt=T
    go.writelog(logfile_fullpath,'Temperature set point = %.2f mK' % (1000*Tsetpt))
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

        go.writelog(logfile_fullpath,wait_msg)
        time.sleep(tot_seconds(temp_wait))
        go.writelog(logfile_fullpath,'reading temperature')
        Tbath=read_bath_temperature(go,logfile_fullpath)
        delta_step=np.abs(Tbath - Tbath_previous)
        Tbath_previous=Tbath
        delta=np.abs(Tbath - T)
        go.writelog(logfile_fullpath,'Tbath=%0.2f mK' %  (1000*go.temperature))

        # check heater percentage
        heatpercent=go.oxford_read_heater_level()
        if heatpercent>99:
            go.writelog(logfile_fullpath,'We need to increase the maximum current to the heater')
            cmdret=go.oxford_increase_heater_range()
            heater=go.oxford_read_heater_range()
            go.writelog(logfile_fullpath,'heater range: %f mA' % heater)
        
    go.writelog(logfile_fullpath,'starting I-V measurement')
    if delta>temp_precision:
        go.writelog(logfile_fullpath,'WARNING! Did not reach target temperature!')
        go.writelog(logfile_fullpath,'Tbath=%0.2f mK, Tsetpoint=%0.2f mK' % (1000*Tbath,1000*T))

    # reset FLL and re-compute the offsets before measurement
    if not TESTMODE:
        go.assign_integration_time(1.0) # int time 1sec for offset calculation
        go.compute_offsets()
        go.feedback_offsets()
        go.configure_PID(I=PID_I) # feedback_offsets() configured the PID.  Now we set it to what we want.
        go.assign_integration_time(timeline_period) 
        if go.get_iv_timeline(vmin=min_bias,vmax=max_bias,frequency=frequency) is None:
            go.writelog(logfile_fullpath,'ERROR! Did not successfully acquire a timeline!')
        else:
            go.write_fits()
            #go.timeline2adu(monitor_TES)
    go.writelog(logfile_fullpath,'end I-V measurement')
    plt.close('all')

    if not TESTMODE:        
        # generate the test document
        go.writelog(logfile_fullpath,'generating test document')
        pdfname=go.make_iv_report()
        go.writelog(logfile_fullpath,'test document generated')

    # reset the plotting figure size
    go.figsize=figsize

    # reset data
    if not TESTMODE:go.adu=None



# finally, switch off the temperature control loop
go.oxford_pidoff()

