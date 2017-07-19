#!/bin/bash

# define where to find the libraries.  Normally it should be in libs.new, one directory up.

BUILD_SH=`echo $0|awk -F/ '{print $NF}'`
PYSTUDIO_RELDIR=`echo $0|sed -ne "s/${BUILD_SH}//" -ep`
LIB_NEW=lib.new

cd $PYSTUDIO_RELDIR
PYSTUDIO_DIR=`pwd -P`
cd ../
if [ ! -d "${LIB_NEW}" ];then
    echo "could not find library directory"
    exit
fi

cd ${LIB_NEW}
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





