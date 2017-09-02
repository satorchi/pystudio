#!/usr/bin/env python
"""
$Id: run_iv.py
$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
$created: Fri 07 Jul 2017 13:45:13 CEST
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

wrapper script to run the I-V curve data gathering
"""
from __future__ import division, print_function
from qubicpack import qubicpack as qp
import matplotlib.pyplot as plt
import sys
reload(sys)
sys.setdefaultencoding('utf8')

def get_from_keyboard(msg,default=None):
    prompt='%s (default: %s) ' % (msg,str(default))
    ans=raw_input(prompt)
    if ans=='':return default
    try:
        x=eval(ans)
    except:
        print('invalid response.')
        return None
    return x
    


go=qp()

# set debuglevel to 1 if you want lots of messages on the screen
# go.debuglevel=1

asic=get_from_keyboard('Which ASIC?  ',2)
if asic==None:quit()
ret=go.assign_asic(asic)

temp=get_from_keyboard('TES bath temperature in K ',0.3)
if temp==None:quit()
ret=go.assign_temperature(temp)
if ret==None:quit()

min_bias=get_from_keyboard('minimum bias voltage ',4.5)
if min_bias==None:quit()
max_bias=get_from_keyboard('maximum bias voltage ',9.0)
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



go.make_Vbias(vmin=min_bias,vmax=max_bias,cycle=cyclebias,ncycles=ncycles,dv=dv)

# run the measurement
go.get_iv_data(TES=70)

# generate the test document
pdfname=go.make_iv_report()
if os.path.exists(pdfname):
    os.system('xpdf %s' % pdfname)

    

