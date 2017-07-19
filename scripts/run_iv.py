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
from qubicpack import qubicpack as qp
import matplotlib.pyplot as plt
go=qp()
go.get_Vavg_data()
raw_input('Hit return to exit. ')
