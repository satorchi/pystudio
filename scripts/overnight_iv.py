#!/usr/bin/env python
'''
$Id: overnight_iv.py
$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
$created: Mon 25 Sep 2017 16:59:04 CEST
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

wrapper script to run several I-V measurements, changing the bath temperature for each one
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

# set this to False for a real measurement
TESTMODE=True

# precision required for bath temperature
temp_precision=0.005 # in Kelvin

# timeout for waiting for temperature to settle
if TESTMODE:
    temp_timeout=dt.timedelta(seconds=30)
    temp_wait=dt.timedelta(seconds=5)
    wait_msg='waiting %.0f seconds for temperature to settle' % tot_seconds(temp_wait)
else:
    temp_timeout=dt.timedelta(minutes=30)
    temp_wait=dt.timedelta(minutes=5)
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
    '''
    handle=open(filename,'a')
    timestamp=dt.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC -- ')
    handle.write(timestamp+msg+'\n')
    handle.close()
    return

go=qp()
figsize=go.figsize

# set debuglevel to 1 if you want lots of messages on the screen
# go.debuglevel=1


'''
get parameters
'''

# can I get ASIC from QubicStudio?
asic=get_from_keyboard('Which ASIC?  ',2)
if asic==None:quit()
ret=go.assign_asic(asic)

# setup bias voltage range
min_bias=get_from_keyboard('minimum bias voltage ',1.0)
if min_bias==None:quit()
max_bias=get_from_keyboard('maximum bias voltage ',3.0)
if max_bias==None:quit()
dv=get_from_keyboard('bias step size ',0.02)
cycle=get_from_keyboard('cycle bias up/down? ','y')
if cycle==None:quit()
if cycle.upper()=='N':
    cyclebias=False
else:
    cyclebias=True
ncycles=get_from_keyboard('number of bias cycles ',3)
if ncycles==None:quit()
monitor_TES=get_from_keyboard('which TES would you like to monitor during the measurement? ',70)
if monitor_TES==None:quit()

go.make_Vbias(vmin=min_bias,vmax=max_bias,cycle=cyclebias,ncycles=ncycles,dv=dv)

# setup temperature range
start_temp=get_from_keyboard('start bath temperature ',0.2)
if start_temp==None:quit()
end_temp=get_from_keyboard('end bath temperature ',0.8)
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

# make a log file
logfile=dt.datetime.utcnow().strftime('temperature_IV_logfile_%Y%m%dT%H%M%SUTC.txt')

# run the measurement
for T in Tbath_target:
    # set the desired bath temperature
    cmdret=go.oxford_set_point(T)
    # make sure the set point was accepted
    Tsetpt=go.oxford_read_set_point()
    if Tsetpt==None:
        writelog(logfile,'ERROR! Could not read set point temperature.')
        Tsetpt=T
    writelog(logfile,'Temperature set point = %.2f mK' % (1000*Tsetpt))
    Tbath=go.oxford_read_bath_temperature()
    if Tbath==None:
        writelog(logfile,'ERROR! Could not read bath temperature.')
        Tbath=go.temperature
    delta=np.abs(Tbath - T)
    start_waiting=dt.datetime.utcnow()
    end_waiting=start_waiting+temp_timeout
    while (delta>temp_precision) and (dt.datetime.utcnow()<end_waiting):
        writelog(logfile,wait_msg)
        time.sleep(tot_seconds(temp_wait))
        writelog(logfile,'reading temperature')
        Tbath=go.oxford_read_bath_temperature()
        if Tbath==None:
            writelog(logfile,'ERROR! Could not read bath temperature.')
            Tbath=go.temperature
        delta=np.abs(Tbath - T)
        writelog(logfile,'Tbath=%0.2f mK' %  (1000*go.temperature))

        # check heater percentage
        heatpercent=go.oxford_read_heater_level()
        if heatpercent>99:
            writelog(logfile,'We need to increase the maximum current to the heater')
            cmdret=go.oxford_increase_heater_range()
            heater=go.oxford_read_heater_range()
            writelog(logfile,'heater range: %f mA' % heater)
        
    writelog(logfile,'starting I-V measurement')
    if delta>temp_precision:
        writelog(logfile,'WARNING! Did not reach target temperature!')
        writelog(logfile,'Tbath=%0.2f mK, Tsetpoint=%0.2f mK' % (1000*Tbath,1000*T))
    go.get_iv_data(TES=monitor_TES,replay=TESTMODE)
    writelog(logfile,'end I-V measurement')
    plt.close('all')

    # generate the test document
    writelog(logfile,'generating test document')
    if not TESTMODE: pdfname=go.make_iv_report()
    writelog(logfile,'test document generated')

    # reset the plotting figure size
    go.figsize=figsize

    # reset data
    if not TESTMODE:go.adu=None



# finally, switch off the temperature control loop
go.oxford_pidoff()

