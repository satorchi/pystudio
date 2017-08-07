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


Installation notes for pystudio
-------------------------------
Note: qubicpack can be installed independently of pystudio.  This is useful if you don't need to connect to QubicStudio.

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


Installation of qubicstudio without pystudio
--------------------------------------------

- Download pystudio as above, but instead of running the build script,
  simply run the qubicpack setup script as follows:

```python
python setup_quibicpack.py install
```

Qubic Pack
----------

authors:
- Steve Torchinsky <satorchi@apc.in2p3.fr>
- Michel Piat
- and other members of the QUBIC team


QubicPack is implemented as a python class with a number of methods.
It is intended to be used with your favourite python environment, such
as ipython or Jupyter.  A simple example of a qubicpack program is the
following:

    >>> from qubicpack import qubicpack
    >>> go=qubipack()
    >>> Vtes=go.get_iv_data()

The above three lines will run the I-V curve measurements for all TES.
Afterwards, you have all the data saved in the qubicpack object.  The
data has also been saved to a file for future analysis offline.

QubicPack can be used to read and plot saved data.  For example, to
plot the I-V curve of TES#70 from data saved on 4 August 2017, do the
following:

    >>> from qubicpack import qubicpack
    >>> go=qubicpack()
    >>> go.read_fits('QUBIC_TES_20170804T134238UTC.fits')
    >>> go.plot_iv(70)

More detailed help is available at https://github.com/satorchi/pystudio/wiki

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

Detailed help
------------

Help documentation can be found on the wiki hosted by GitHub:
https://github.com/satorchi/pystudio/wiki

