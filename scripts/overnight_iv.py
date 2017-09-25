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
reload(sys)
sys.setdefaultencoding('utf8')

# precision required for bath temperature
temp_precision=0.005 # in Kelvin

# timeout for waiting for temperature to settle
temp_timeout=dt.timedelta(minutes=30)

def get_from_keyboard(msg,default=None):
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
    


go=qp()

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
min_temp=get_from_keyboard('minimum bath temperature ',0.2)
if min_temp==None:quit()
max_temp=get_from_keyboard('maximum bath temperature ',0.8)
if max_temp==None:quit()
step_temp=get_from_keyboard('temperature steps',0.025)
if step_temp==None:quit()

Tbath_target=np.arange(min_temp,max_temp,step_temp)

# run the measurement
for T in Tbath_target:
    Tbath=go.oxford_read_bath_temperature()
    delta=np.abs(Tbath - T)
    start_waiting=dt.datetime.utcnow()
    end_waiting=start_waiting+temp_timeout
    while (delta>temp_precision) and (dt.datetime.utcnow()<end_waiting):
        print('waiting 5 minutes for temperature to settle...')
        time.sleep(300)
        print(' reading temperature: ')
        Tbath=go.oxford_read_bath_temperature()
        delta=np.abs(Tbath - T)
        print('Tbath=%0.2f mK\n' % (1000*go.temperature))
        
        
    
go.get_iv_data(TES=monitor_TES)

# generate the test document
pdfname=go.make_iv_report()

# find pdf viewer
viewers=['xpdf','evince','okular','acroread']
use_viewer=None
for viewer in viewers:
    cmd='which %s' % viewer
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    if not out=='':
        use_viewer=out.strip()
        break
        
cmd='%s %s' % (use_viewer,pdfname)
if not pdfname==None and os.path.exists(pdfname) and not use_viewer==None:
    os.system(cmd)

    

