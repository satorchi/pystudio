'''
$Id: modulator.py
$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
$created: Thu 07 Dec 2017 13:13:27 CET
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

send commands to the HP33120A wave form generator
This is used to modulate the calibration source
'''
from __future__ import division, print_function
import serial,time


def init_hp22130a(self,port='/dev/ttyS0'):
    '''
    establish connection to the HP22130A waveform generator
    It should be connected by RS232 cable (serial port, usually /dev/ttyS0)
    '''

    s=serial.Serial(port=port,
                    baudrate=9600,
                    bytesize=8,
                    parity='N',
                    stopbits=1,
                    timeout=10,
                    xonxoff=True,
                    rtscts=False)

    print('Establishing communication with the HP22130A wave generator.')
    s.write('*IDN?\n')
    id=s.readline()
    if id=='':
        print('ERROR! unable to communicate!')
        return None

    print('The device says: %s' % id)

    s.write('\n*CLS\n')
    time.sleep(0.5)
    s.write('SYST:REM\n')

    self.modulator=s
    return s

def modulator_frequency(self,frequency=100.0,form='SIN',amplitude=0.1):
    '''
    set the modulation frequency on the HP33120A waveform generator
    '''

    cmd='APPL:%s %.5E, %.2f\n' % (form,frequency,amplitude)
    s.write(cmd)
    return


