# pystudio - Qubic Studio for Python

A Python interface for Qubic Studio
* originally implemented by Pierre Chanial
* current maintainer: Steve Torchinsky <satorchi@apc,in2p3.fr>

QubicStudio is the control software for QUBIC
developed by Wilfried Marty at IRAP


# Introduction

pystudio is a python interface to QubicStudio allowing remote access
to the QUBIC local control computer.  All the power of python is
available to perform, record, and analyze complex measurements.  The
package QubicPack (see below) is a collection of tools to run various
measurements and analyze them in real-time.

# Qubic Pack

authors: 
* Steve Torchinsky <satorchi@apc.in2p3.fr>
* Michel Piat
* and other members of the QUBIC team


QubicPack is implemented as a python class with a number of methods.
It is intended to be used with your favourite python environment, such
as ipython or jupyter.  A simple example of a qubicpack program is the
following:

    >>> from qubicpack import qubicpack
    >>> go=qubipack()
    >>> Vtes=go.get_IV_data()

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