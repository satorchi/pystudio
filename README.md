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
     $ git clone https://github.com/satorchi/pystudio.git
     $ cd pystudio
     $ ./build.sh
     $ sudo python ./setup.py install
```

and run pystudio!  You will also want [QubicPack](https://github.com/satorchi/qubicpack)


