#!/usr/bin/env python
'''
$Id: fast_iv.py
$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
$created: Mon 30 Oct 2017 08:31:17 CET
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

wrapper script to run an I-V measurement using the "fast" method
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

go=qp()
go.debuglevel=1


# can I get ASIC from QubicStudio?
asic=go.get_from_keyboard('Which ASIC?  ',2)
if asic==None:quit()
ret=go.assign_asic(asic)

monitor_TES=go.get_from_keyboard('which TES would you like to monitor during the measurement? ',64)
if monitor_TES==None:quit()

go.assign_integration_time(240)
#go.configure_PID()
# Fri 19 Jan 2018 14:19:58 CET: we removed the 5x bias factor
go.get_iv_timeline(vmin=3.0,vmax=9.0)

go.timeline2adu(monitor_TES)

go.write_fits()
#go.plot_iv(monitor_TES)
