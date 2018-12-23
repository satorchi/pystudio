#!/usr/bin/env python
'''
$Id: run_bot.py
$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
$created: Thu 20 Dec 2018 17:43:37 CET
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

run the QUBIC telegram bot
'''
import os,sys
import matplotlib
matplotlib.use('Agg')

from qubicpack.hk.qubic_bot import qubic_bot

TESTMODE=False
for arg in sys.argv:
    if arg=='--test':TESTMODE=True

qb = qubic_bot(test=TESTMODE)

