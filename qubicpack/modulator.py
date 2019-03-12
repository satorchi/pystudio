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
import serial,time,os,sys
import readline
readline.parse_and_bind('tab: complete')
readline.parse_and_bind('set editing-mode vi')

from PyMS import PMSDevice

class modulator:
    '''
    class to send commands to the HP3312A signal generator
    '''

    def __init__(self,port='/dev/rs232_1'):
        self.energenie = None
        self.default_settings = {}
        self.default_settings['frequency'] = 0.333
        self.default_settings['shape'] = 'SQU'
        self.default_settings['amplitude'] = 5.0
        self.default_settings['offset'] = 2.5
        self.default_settings['duty'] = 33.0

        self.s = None
        self.port = port
        return None

    def is_connected(self):
        '''
        check if the signal generator is connected
        '''
        if self.s is None:
            # try to connect
            self.init_hp33120a()

        if self.s is None:
            return False
        
        self.s.write('*IDN?\n')
        id = self.s.readline()
        if id=='':  return False        
        
        return True
    
    def switchon(self):
        '''
        use the Energenie smart powerbar to switch on the power to the modulator
        '''

        # open Energenie device with hostname and password
        if self.energenie is None:
            self.energenie = PMSDevice('energenie', '1')

        # switch on
        self.energenie.set_socket_states({0:True})

        return

    def switchoff(self):
        '''
        use the Energenie smart powerbar to switch off the power to the modulator
        '''

        # open Energenie device with hostname and password
        if self.energenie is None:
            self.energenie = PMSDevice('energenie', '1')

        # switch on
        self.energenie.set_socket_states({0:False})

        return    
        

    def init_hp33120a(self,port=None):
        '''
        establish connection to the HP33120A waveform generator
        It should be connected by RS232 cable (serial port, usually /dev/ttyS0)

        We can use port=/dev/hp33120a

        put the following in /etc/udev/rules.d/hp33120a.rules

        SUBSYSTEM=="tty", ATTRS{idVendor}=="067b", ATTRS{idProduct}=="2303",
        OWNER="qubic", GROUP="users", MODE="0666", SYMLINK+="hp33120a"

        or the cable rs232/usb 

        SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", 
        OWNER="qubic", GROUP="users", MODE="0664", SYMLINK+="rs232"

        '''
        if port is None: port = self.port
        if port is None: port = '/dev/rs232'
    
        # check of the requested device exists
        if not os.path.exists(port):
            print('Cannot connect to device.  Device does not exist: %s' % port)
            return None

        s=serial.Serial(port=port,
                        baudrate=9600,
                        bytesize=8,
                        parity='N',
                        stopbits=1,
                        timeout=0.5,
                        xonxoff=True,
                        rtscts=False)

        print('Establishing communication with the HP33120A wave generator on port %s' % port)
        s.write('*IDN?\n')
        id=s.readline()
        if id=='':
            print('ERROR! unable to communicate!')
            return None

        print('The device says: %s' % id)

        s.write('\n*CLS\n')
        time.sleep(0.5)
        s.write('SYST:REM\n')
        time.sleep(0.5)

        self.s=s
        return s

    def configure(self,frequency=None,shape=None,amplitude=None,offset=None,duty=None,port=None):
        '''
        configure the HP33120A waveform generator
        
        Frequency is given in Hz
        The wave form can be: SIN, SQU, TRI,     
        '''

        if self.s is None:
            s=self.init_hp33120a(port=port)
            if s is None:return False

        # set default values if *no* options given
        if frequency is None\
           and shape is None\
           and amplitude is None\
           and offset is None\
           and duty is None:
            settings = self.default_settings
        else:        
            # read the current values for the default values if necessary
            settings = self.read_settings(show=False)
            
        # if something went wrong with reading, use the default values
        if settings is None:
            settings = self.default_settings
            
        if frequency is None:
            frequency=settings['frequency']
        if shape is None:
            shape=settings['shape']
        if amplitude is None:
            amplitude=settings['amplitude']
        if offset is None:
            offset=settings['offset']
        if duty is None:
            duty=settings['duty']

        # fix a common error in the shape.  I sometimes write "sqr" instead of "squ"
        if shape.upper().find('SQ') >= 0: shape='SQU'

        cmd='APPL:%s %.5E, %.2f, %.2f\n' % (shape.upper(),frequency,amplitude,offset)
        self.s.write(cmd)
        time.sleep(0.5)
        cmd='PULS:DCYC %.2f\n' % duty
        self.s.write(cmd)
        time.sleep(0.5)
        return True

    def set_default_settings(self):
        '''
        configure with default settings
        '''
        return self.configure()

    def read_settings(self,show=True):
        '''
        read the current settings of the HP33120a waveform generator
        '''

        if self.s is None:
            s=self.init_hp33120a()
            if s is None:return None

        self.s.write('APPL?\n')
        ans=self.s.readline().strip()
        if  not ans:
            print('signal generator appears to be off')
            return None
        
        vals=ans.replace('"','').split()
        settings={}
        try:
            settings['shape']=vals[0]
        except:
            print("what is wrong here? received ans=%s" % vals)
            return None
        
        try:
            val=vals[1].split(',')
            settings['frequency']=eval(val[0])
            settings['amplitude']=eval(val[1])
            settings['offset']   =eval(val[2])
        except:
            print("Could not read signal generator settings: %s" % vals)
            return None
            
            
        self.s.write('PULS:DCYC?\n')
        ans=self.s.readline()
        val=ans.strip()
        try:
            settings['duty']=eval(val)
        except:
            print('Could not read the signal generator duty cycle: %s' % val)
            return None
        
        if show:
            print('SHAPE: %s\nFREQUENCY: %.6f Hz\nAMPLITUDE: %.6f V\nOFFSET: %.6f V\nDUTY CYCLE: %.1f%%' % \
                  (settings['shape'],settings['frequency'],settings['amplitude'],settings['offset'],settings['duty']))
        return settings
        
    def read_frequency(self):
        '''
        read the current frequency setting of the HP33120A waveform generator
        '''

        if self.s is None:
            s=self.init_hp33120a()
            if s is None:return False
        
    
        self.s.write('FREQ?\n')
        freq_str=self.s.readline()
        freq=eval(freq_str.strip())
        print('HP33120A is set to %.6f Hz' % freq)
        return freq

    def read_shape(self):
        '''
        read the current modulation shape setting of the HP33120A waveform generator
        '''

        if self.s is None:
            s=self.init_hp33120a()
            if s is None:return False
        
    
        self.s.write('FUNC:SHAPE?\n')
        shape=self.s.readline().strip()
        print('HP33120A is running a %s modulation' % shape)
        return shape

    def read_duty(self):
        '''
        read the duty cycle
        '''
        if self.s is None:
            s=self.init_hp33120a()
            if s is None:return False
        
    
        self.s.write('PULS:DCYC?\n')
        ans=self.s.readline()
        val=ans.strip()
        duty=eval(val)
        print('HP33120A is running a %.1f%% duty cycle' % duty)
        return duty
        

    def run_commands(self,parms):
        '''
        run a list of commands given by the dictionary "parms"

        parms.keys() should have all the keywords used in self.configure()
        '''

        # some debug text
        #print("here are the commands I've received:\n")
        #for key in parms.keys():
        #    print('  %s: %s\n' % (key,parms[key]))
        

        
        if parms['help']:
            self.help()
            return
        
        if parms['onoff'] == 'on':
            self.switchon()
            return

        if parms['onoff'] == 'off':
            self.switchoff()
            return

        if parms['default']:
            self.configure()
            return
        
        if parms['status'] == 'show':
            self.read_settings(show=True)
            return
        
        self.configure(frequency=parms['frequency'],
                       shape=parms['shape'],
                       amplitude=parms['amplitude'],
                       offset=parms['offset'],
                       duty=parms['duty'])

        time.sleep(0.2)
        self.read_settings(show=True)
        return

    def parseargs(self,argslist):
        '''
        interpret a list of commands and return a dictionary of commands to use in run_commands()
        '''
        
        # initialize
        parms = {}
        numerical_keys = ['frequency','freq','f','amplitude','a','offset','o','duty','d']
        str_keys = ['shape','sh','status','onoff','quit','default','help']
        keys = numerical_keys + str_keys
        for key in keys:
            parms[key]=None

        # if no arguments, just show status
        if not argslist:
            parms['status'] = 'show'

        # parse argslist
        for arg in argslist:
            arg = arg.lower()
            for key in numerical_keys:
                findstr = '%s=' % key
                if arg.find(findstr)==0:
                    if key=='freq' or key=='f':
                        key='frequency'
                    if key=='a': key='amplitude'
                    if key=='o': key='offset'
                    if key=='d': key='duty'
                    if key=='s': key='status'
                    if key=='sh': key='shape'
                    vals = arg.split('=')
                    try:
                        val = eval(vals[1])
                        parms[key] = val
                            
                    except:
                        print('invalid %s' % key)

            for key in str_keys:
                findstr = '%s=' % key
                if arg.find(findstr)==0:
                    vals = arg.split('=')
                    val = vals[1].upper()
                    parms[key] = val

            # toggle type keywords
            if arg=='status':
                parms['status'] = 'show'
                continue

            if arg=='default' or arg=='init':
                parms['default'] = True
                continue
            
            if arg=='on':
                parms['onoff'] = 'on'
                continue

            if arg=='off':
                parms['onoff'] = 'off'
                continue

            if arg=='q' or arg=='quit' or arg=='exit':
                parms['quit'] = True
                continue

            if arg=='help' or arg=='h':
                parms['help'] = True
                continue

        return parms

    def help(self):
        '''
        print some help about valid commands
        '''
        helptxt =  '\ncommands:\n'
        helptxt += '\nfrequency=<N> : frequency is given in Hz (default 1Hz)'
        helptxt += '\namplitude=<N> : amplitude in V (default 5V)'
        helptxt += '\noffset=<N>    : offset in V (default 2.5V)'
        helptxt += '\nduty=<N>      : duty cycle in percent (default 50%)'
        helptxt += '\nshape=<S>     : shape is one of "SQU, SIN, TRI (default SQU)'
        helptxt += '\ndefault       : setup default values for the signal generator'
        helptxt += '\nstatus        : print out the current settings'
        helptxt += '\non            : switch on the signal generator'
        helptxt += '\noff           : switch off the signal generator'
        helptxt += '\nquit          : quit the program'

        print(helptxt)
                
        return

    def command_loop(self,argstr=None):
        '''
        a command line interface to the modulator
        '''

        # initially, use command line arguments at invocation
        if argstr is None:
            argslist = sys.argv
        else:
            argslist = argstr.strip().split()
        
        parms = self.parseargs(argslist)
        while not parms['quit']:
            self.run_commands(parms)
            ans=raw_input('Enter command ("help" for list): ')
            argslist = ans.strip().split()
            parms = self.parseargs(argslist)

        return


        
            
        
    
