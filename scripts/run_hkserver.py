#!/usr/bin/env python
'''
$Id: run_hkserver.py
$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
$created: Tue 11 Dec 2018 09:22:58 CET
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

run the server for sending QUBIC housekeeping data over socket
'''
import os
import matplotlib
matplotlib.use('Agg')

from qubicpack.hk.hk_broadcast import hk_broadcast

if 'HOME' in os.environ.keys():
    homedir = os.environ['HOME']
else:
    homedir = os.path.curdir

broadcast_dir = homedir + os.sep + os.sep.join(['data','temperature','broadcast'])
if not os.path.isdir(broadcast_dir):
    os.system('mkdir %s' % broadcast_dir)

os.chdir(broadcast_dir)

# now start the server
bc=hk_broadcast()
bc.hk_server()
