#!/usr/bin/env python
'''
$Id: iv_analysis_example.py
$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
$created: Mon 05 Mar 2018 07:40:56 CET
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

This is an example script for analysing the QUBIC I-V measurement
You can run this in ipython, or Jupyter notebook.
'''


'''
Before beginning, you should have pystudio installed, and copy the example data files.

You will also need my datefunctions module

### INSTALLATION OF pystudio ###

get the package from github

$ git clone https://github.com/satorchi/pystudio.git
$ cd pystudio
$ sudo python ./setup.py install

$ cd ../
$ git clone https://github.com/satorchi/mypy.git
$ cd mypy
$ sudo python ./setup.py install

### Data files ###
You should copy the following data files into your working directory

QUBIC_timeline_20180301T184953UTC.fits
QUBIC_timeline_20180301T212734UTC.fits

'''

# import necessary  stuff
import os
import matplotlib.pyplot as plt
from qubicpack import qubicpack as qp
from qubicpack.temperature_analysis import *
from qubicpack.plot_physical_layout import *
import datetime as dt


# create the qubicpack object and read the data
d0=qp()

# the first data file contains measurements at high temperature
# these are used to correct the Normal Resistance
d0.read_fits('QUBIC_timeline_20180301T184953UTC.fits')

# The data contains multiple timelines at different temperatures
# you can print out a summary table
print_datlist(d0)

# we will work with the first timeline which is at 601mK
# (we set timeline_index=0)

# first of all, have a look at all timelines for all the TES
d0.plot_timeline_physical_layout(timeline_index=0)

# now look at one in particular.  TES=85
# the plot will determine the period and phase of the sinusoidal bias voltage
d0.plot_timeline(85,timeline_index=0)

# the bias is now set for all the TES, and we can plot the I-V curves
# but first, we should run the filter which fits a model to each TES I-V curve
f=d0.filter_iv_all()

# now plot all the I-V curves
d0.plot_iv_physical_layout()

# Now we will save the list of Normal Resistances which will be used to correct the I-V curves at lower temperature
R1adjust=d0.R1()

# Next we will read the data at cooler temperatures

# create a new qubicpack object, and read the data
d1=qp()
d1.read_fits('QUBIC_timeline_20180301T212734UTC.fits')

# have a look a the summary
print_datlist(d1)

# it is also possible to look at a summary of multiple qubicpack objects by making a list
datlist=[d0,d1]
print_datlist(datlist)

# let's plot the I-V curves for Tbath=360mK.  This is for timeline_index=2
# first, we look at the timelines
d1.plot_timeline_physical_layout(timeline_index=2)

# and let's look at one TES in particular, TES=85
d1.plot_timeline(85,timeline_index=2)

# Now we have the bias for the whole array, and we can plot all the I-V
# but first we run the filter to make the model fit to the I-V curves
# we also apply the Normal Resistance correction which we saved earlier (R1adjust)
# we also choose limits which will flag the TES as good or bad
# These include:  bias_margin, relative amplitude limit, and absolute amplitude limit.
#                 We choose values which are not too stringent
f=d1.filter_iv_all(bias_margin=-3,rel_amplitude_limit=1e-6,abs_amplitude_limit=1e-6,R1adjust=R1adjust)

# now we can plot the I-V curves.
d1.plot_iv_physical_layout()


# Now let's look at a temperature where everything doesn't behave perfectly
# we will need to do some adjustments before plotting the I-V curves

# Let's look at timeline_index=4, which is for Tbath=320mK.
# We look at TES=85 again
d1.plot_timeline(85,timeline_index=4)

# As you can see, the model of the bias is not correct.
# This is because we still have the previous model in memory
# In order to replace the memory with a new bias model, we run "timeline2adu" for our chosen example
d1.timeline2adu(85,timeline_index=4)

# Now plot the timeline again, it looks much better!
d1.plot_timeline(85,timeline_index=4)

# But, now plot the corresponding I-V curve.  There is something wrong!
d1.plot_iv(85)

# It's backwards!  This happens sometimes because the algorithm is not clever enough to find the correct bias model.
# We can adjust it manually by shifting the bias curve by a half a period.
# We re-run timeline2adu, but with a shift:
d1.timeline2adu(85,timeline_index=4,shift=0.5)

# Now replot the timeline, and you can see the bias model has been shifted
d1.plot_timeline(85,timeline_index=4)

# And replot the I-V curve, but first, rerun the filter to model the I-V curve
f=d1.filter_iv(85)
d1.plot_iv(85)

# The I-V curve looks much better!
# Now apply the filter to all the TES
f=d1.filter_iv_all(bias_margin=-3,rel_amplitude_limit=1e-6,abs_amplitude_limit=1e-6,R1adjust=R1adjust)

# and plot all the I-V curves
d1.plot_iv_physical_layout()

# Let's produce a full report for the I-V curves at 320mK
# this will take a few minutes to run as it will produce all the necessary plots
texfile=d1.make_iv_report()

