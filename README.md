# pystudio

pystudio - Qubic Studio for Python
==================================

A Python interface for Qubic Studio
- originally implemented by Pierre Chanial
- current maintainer: Steve Torchinsky <satorchi@apc,in2p3.fr>

QubicStudio is the control software for QUBIC
developed by Wilfried Marty at IRAP


Introduction
------------

pystudio is a python interface to QubicStudio allowing remote access
to the QUBIC local control computer.  All the power of python is
available to perform, record, and analyze complex measurements.  The
package QubicPack (see below) is a collection of tools to run various
measurements and analyze them in real-time.


Installation notes
------------------

- The files parametersDescription.dispatcher and parametersTF.dispatcher
must be copied into the directory that contains the python interpreter
(the actual python executable). These files are not used by the pystudio
code, but by the dispatchertf library.

- The environment variable LIBDISPATCHERACCESS can be set to the path of
 an alternative directory containing the Qubic Studio libraries.

- If the QT5 headers are not in the standard directory /usr/include/qt5 and
if the utility pkg-config is not installed, the environment variable QTPATH
can be used to specify

- The source code for pystudio and qubicpack is available from GitHub:
https://github.com/satorchi/pystudio

- Download pystudio and use the build.sh script

```bash
     $ git clone git@github.com:satorchi/pystudio.git
     $ cd pystudio
     $ ./build.sh
     $ sudo python ./setup.py install
```

and run pystudio!  See the description of QubicPack below for more details.

Qubic Pack
----------

authors:
- Steve Torchinsky <satorchi@apc.in2p3.fr>
- Michel Piat
- and other members of the QUBIC team


QubicPack is implemented as a python class with a number of methods.
It is intended to be used with your favourite python environment, such
as ipython or jupiter.  A simple example of a qubicpack program is the
following:

    >>> from qubicpack import qubicpack
    >>> go=qubipack()
    >>> Vtes=go.get_Vavg_data()

The above three lines will run the I-V curve measurements for all TES.
Afterwards, you have all the data saved in the qubicpack object.  The
data has also been saved to a file for future analysis offline.  More
examples are given below, including details on each method available
in QubicPack.

QubicPack is installed on the computer in the Millimetre Lab at APC.
The machine is called LaboMM.  As of this writing, the machine has IP
address: 134.158.187.56.  This machine is accessible remotely, and
QUBIC can be controlled by making an ssh connection to LaboMM and
running your QubicPack python scripts.  Any machine within the APC
network can run pystudio and QubicPack to communicate with the Local
Control Computer.  QubicPack can also be used offline to work with
data previously saved.

A QubicPack object (called "go" in the example above) has a number of
methods and internal variables which are required to run measurements.
Once you create a QubicPack object, the parameters will have their
default values.  Changing a parameter, such as the integration time,
for example, will make the change available to all the methods which
use integration time, so that you don't have to reset the parameter
for every type of measurement.

Here is a list of QubicPack methods:


assignment methods
------------------

Assignment methods are intended to assign valid values to various
parameters.  It's good practice to use these methods rather than
assigning through a back-door (knowing that Python does not have
"private" variables).

assign_defaults()
 - assign default values to parameters
 
assign_asic(asic)
 - assign which ASIC is in communication (which half of the 256 TES array)
 
assign_integration_time(tinteg)
 - integration time for data gathering
 
assign_pausetime(pausetime)
 - wait time between subsequent commands to QubicStudio
 
assign_ip(ip)
 - IP address of the QUBIC Local Control Computer (running QubicStudio)


Data gathering and visualization
--------------------------------

wait_a_bit(pausetime)
 - pause before continuing
 
ADU2I(ADU, offset=None, fudge=1.0)
 - conversion from the Analogue Digital Units returned by QubicStudio to current in micro Ampere

find_offset(I,Vbias)
 - find the offset required to make the I-V curve have an equivalent circuit of 1 Ohm

setup_plot_Vavg(axes=None)
 - setup the window, axes, etc for a running plot during I-V measurement
 
plot_Vavg(Vavg,Vbias,offset=None,axes=None)
 - plot the current output for each TES.  This method is used by get_Vavg_data().  see below.

make_line(pt1,pt2,xmin,xmax)
 - find the end points of a line at xmin and xmax given points pt1 and pt2
 
draw_iv(I,colour='blue')
 - draw the I-V curve on the plot
 
plot_iv(TES=None,offset=None,fudge=1.0,multi=False)
 - make a plot of an I-V curve, or multiple curves
 - if TES=None, all I-V curves are plotted on top of each other
 - if multi=True, a grid of plots is made, one for each TES
 
make_Vbias(cycle_voltage=True,vmin=5.0,vmax=8.0,dv=0.04,lowhigh=True):
 - make the list of bias voltages used during the I-V curve measurement
 
get_Vavg_data(self):

filter_Vtes(self):

read_Vtes_file(filename):

heres_one_I_made_earlier(filename=None, axes=None):

connect_QubicStudio(client=None, ip=None):

get_amplitude(integration_time=None, asic=None):

get_mean(integration_time=None, asic=None):

integrate_scientific_data(integration_time=None, asic=None):

set_VoffsetTES(tension, amplitude, asic=0):

set_diffDAC(tension):

set_slowDAC(tension):




