#!/usr/bin/env python
'''
$Id: run_hkclient.py
$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
$created: Tue 11 Dec 2018 09:23:51 CET
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

run the client for gathering QUBIC housekeeping data sent on the socket
'''
import matplotlib
matplotlib.use('Agg')

from qubicpack.hk.hk_broadcast import hk_broadcast
bc=hk_broadcast()
bc.hk_client()
