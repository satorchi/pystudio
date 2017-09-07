# Simple script to set the frequency of the QUBIC calibration source 
# Written by Manuel Gonzalez (manuel.gonzalez@ib.edu.ar), 2017

import sys
if(len(sys.argv)!=2):
    print("Error: no frequency to set")
    print("Usage: python setf.py f")
    exit()
f=float(sys.argv[1])
if(f<110 or f>170):
    print("Error: frequency out of range (110 - 170 GHz)")
    exit()
else:
    print("Setting Frequency:", f, "GHz...")

import serial
source = serial.Serial('/dev/ttyUSB0') 

# TODO If this is going to be implemented in a Raspberry pi that controls both sources udev rules should be defined in order to be able to identify them

def setFreqCommand(f):
    a=[6,70]
    for i in range(5):
        a.append(int(f))
        f=f % 1
        f*=256
    b=a[0]
    for i in a[1:]:
        b=b^i
    a.append(b)
    c = bytearray(a)
    return c

def outputFrequency(response):
    result = ''
    for i in response[1:]:
            result+=format(i,'08b') 
            j=1
            s=0
            for i in result:
                if(int(i)):
                    s+=2**(-j)
                j+=1
    return (s+response[0])*24

command=setFreqCommand(f/12.)
source.write(command)
response=source.read(6)
if(response[0]==85):
    print("OK")
    of=outputFrequency(response[1:])
    print("The output frequency is", of, "GHz")
else:
    print("communication error")
    of=outputFrequency(response[1:])
    print("The output frequency is", of, "GHz")
