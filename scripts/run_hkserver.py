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
from qubicpack.hk.hk_broadcast import hk_broadcast
bc=hk_broadcast()
bc.hk_server()
