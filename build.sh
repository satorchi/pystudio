#!/bin/bash
# $Id: build.sh
# $auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
# $created: Wed 19 Jul 2017 15:32:22 CEST
# $license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt
# 
#           This is free software: you are free to change and
#           redistribute it.  There is NO WARRANTY, to the extent
#           permitted by law.
#
# wrapper script to build the pystudio and qubicpack packages
# this is a bit of a hack to ensure we correctly point to the QubicStudio libraries
#
# Note that this wrapper does a full clean and rebuilds the package!

BUILD_SH=`echo $0|awk -F/ '{print $NF}'`
PYSTUDIO_RELDIR=`echo $0|sed -ne "s/${BUILD_SH}//" -ep`

cd $PYSTUDIO_RELDIR
PYSTUDIO_DIR=`pwd -P`
QUBICSTUDIO_LIB=QubicStudio.lib

if [ ! -d "${QUBICSTUDIO_LIB}" ];then
    echo "could not find library directory!  $QUBICSTUDIO_LIB"
    exit
fi

cd ${QUBICSTUDIO_LIB}
LIBDISPATCHERACCESS=`pwd -P`

cd $PYSTUDIO_DIR

python ./setup.py clean
rm -fv pystudio/pystudio.cpp
LIBDISPATCHERACCESS=${LIBDISPATCHERACCESS}\
		   CFLAGS="-std=c++11"\
		   python ./setup.py build

export LD_LIBRARY_PATH=$LIBDISPATCHERACCESS

echo "Before running python with pystudio, you may need to define LD_LIBRARY_PATH"
echo "export LD_LIBRARY_PATH=${LIBDISPATCHERACCESS}"





