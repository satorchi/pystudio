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
import serial,time,os


def init_hp33120a(self,port='/dev/hp33120a'):
    '''
    establish connection to the HP33120A waveform generator
    It should be connected by RS232 cable (serial port, usually /dev/ttyS0)

    We can use port=/dev/hp33120a

    put the following in /etc/udev/rules.d/hp33120a.rules

    SUBSYSTEM=="tty", ATTRS{idVendor}=="067b", ATTRS{idProduct}=="2303", OWNER="qubic", GROUP="users", MODE="0666", SYMLINK+="hp33120a"
    '''

    # check of the requested device exists
    if not os.path.exists(port):
        print('ERROR! Cannot connect to device.  Device does not exist: %s' % port)
        return None
    
    s=serial.Serial(port=port,
                    baudrate=9600,
                    bytesize=8,
                    parity='N',
                    stopbits=1,
                    timeout=0.5,
                    xonxoff=True,
                    rtscts=False)

    print('Establishing communication with the HP33120A wave generator.')
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

def modulator_configure(self,frequency=None,shape=None,amplitude=None,offset=None,duty=None,port='/dev/rs232'):
    '''
    configure the HP33120A waveform generator

    Frequency is given in Hz
    The wave form can be: SIN, SQU, TRI,     
    '''

    if self.modulator is None:
        s=self.init_hp33120a(port=port)
        if s is None:return False

    # default values
    if frequency is None and shape is None and amplitude is None and offset is None and duty is None:
        frequency=1.0
        shape='SQU'
        amplitude=5.0
        offset=2.5
        
    # read the current values for the default values if necessary
    settings=self.modulator_settings(show=False)
    if frequency is None:
        frequency=settings['frequency']
    if shape is None:
        shape=settings['shape']
    if amplitude is None:
        amplitude=settings['amplitude']
    if offset is None:
        offset=settings['offset']
    if duty is None:
        duty=settings['dutycycle']

    # fix a common error in the shape.  I sometimes write "sqr" instead of "squ"
    if shape.upper().find('SQ') >= 0: shape='SQU'

    
    cmd='APPL:%s %.5E, %.2f, %.2f\n' % (shape.upper(),frequency,amplitude,offset)
    self.modulator.write(cmd)
    cmd='PULS:DCYC %.2f\n' % duty
    self.modulator.write(cmd)
    return True

def modulator_settings(self,show=True):
    '''
    read the current settings of the HP33120a waveform generator
    '''

    if self.modulator is None:
        s=self.init_hp33120a()
        if s is None:return None

    self.modulator.write('APPL?\n')
    ans=self.modulator.readline()
    vals=ans.strip().replace('"','').split()
    settings={}
    settings['shape']=vals[0]
    val=vals[1].split(',')
    settings['frequency']=eval(val[0])
    settings['amplitude']=eval(val[1])
    settings['offset']   =eval(val[2])
    self.modulator.write('PULS:DCYC?\n')
    ans=self.modulator.readline()
    val=ans.strip()
    settings['dutycycle']=eval(val)
    if show:
        print('SHAPE: %s\nFREQUENCY: %.2f Hz\nAMPLITUDE: %.3f V\nOFFSET: %.3f V\nDUTY CYCLE: %.1f%%' % \
              (settings['shape'],settings['frequency'],settings['amplitude'],settings['offset'],settings['dutycycle']))
    return settings
        
def modulator_frequency(self):
    '''
    read the current frequency setting of the HP33120A waveform generator
    '''

    if self.modulator is None:
        s=self.init_hp33120a()
        if s is None:return False
        
    
    self.modulator.write('FREQ?\n')
    freq_str=self.modulator.readline()
    freq=eval(freq_str)
    print('HP33120A is set to %.2f Hz' % freq)
    return freq

def modulator_shape(self):
    '''
    read the current modulation shape setting of the HP33120A waveform generator
    '''

    if self.modulator is None:
        s=self.init_hp33120a()
        if s is None:return False
        
    
    self.modulator.write('FUNC:SHAPE?\n')
    shape=self.modulator.readline()
    print('HP33120A is running a %s modulation' % shape)
    return shape

