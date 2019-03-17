'''
$Id: calsource_configuration_manager.py
$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
$created: Fri 08 Feb 2019 08:25:47 CET
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

A class with methods to send/receive configuration command for the calibration source setup
Commands are sent to switch on/off and configure three components: calsource, amplifier, modulator
'''
from __future__ import division, print_function
import socket,subprocess,time,re,os,multiprocessing
import datetime as dt

import readline
readline.parse_and_bind('tab: complete')
readline.parse_and_bind('set editing-mode vi')

# the Energenie powerbar
from PyMS import PMSDevice

# the calibration source
from qubicpack.calibration_source import calibration_source

# the signal generator for modulating the calibration source
from qubicpack.modulator import modulator

# the Arduino Uno
from qubicpack.arduino import arduino

from satorchipy.datefunctions import tot_seconds

class calsource_configuration_manager():

    def __init__(self,role=None):
        '''
        initialize the object.  The role can be either "commander" or "manager"
        The "manager" runs on the Raspberry Pi, and interfaces directly with the hardware
        The "commander" sends commands via socket to the "manager"
        '''
        self.assign_variables(role)
        if self.role == 'manager':
            self.listen_loop()
        else:
            self.command_loop()
            
        return None

    def log(self,msg):
        '''
        log message to screen and to a file
        '''
        filename = 'calsource_configuration_%s.log' % self.role
        h=open(filename,'a')
        h.write('%s: %s\n' % (dt.datetime.utcnow().strftime(self.date_fmt),msg))
        h.close()
        print(msg)
        return

    def command_help(self):
        '''
        print some help text to screen
        '''
        device_list_str = ', '.join(self.device_list)
        txt  = 'Calibration Source Commander:  Help\n'
        txt += 'commands should be given in the following format:\n'
        txt += '    <device>:<parameter>[=<value>]\n\n'
        txt += 'except for the following commands which are independent of device: help, status, on, off, save\n\n'
        txt += 'valid devices: %s\n' % device_list_str
        for dev in self.device_list:
            valid_commands = ', '.join(self.valid_commands[dev])
            txt += 'valid commands for %s: %s\n' % (dev,valid_commands)
        txt += '\nFor the modulator, frequency is given in Hz\n'
        txt += 'For the calibration source, frequency is given in GHz\n'
        txt += '\nFor the arduino, duration is given in seconds.\n'
        txt += 'Note that this command will immediately start an acquisition.\n'
        txt += '\nExample:\n'
        txt += 'calsource:on amplifier:on modulator:on modulator:frequency=0.333 modulator:duty=33 modulator:shape=squ calsource:frequency=150\n'
        print(txt)
        return
    
    def assign_variables(self,role):
        '''
        initialize variables, depending on the role
        if the role is "manager", we need to connect to the hardware
        '''
        self.role = role
        self.date_fmt = '%Y-%m-%d %H:%M:%S.%f'
        self.device_list = ['modulator','calsource','lamp','amplifier','arduino']
        self.amp_on = None   # need to find a way to detect this
        self.lamp_on = None  # need to find a way to detect this

        self.valid_commands = {}
        self.valid_commands['modulator'] = ['on','off','frequency','amplitude','offset','duty','shape']
        self.valid_commands['calsource'] = ['on','off','frequency']
        self.valid_commands['amplifier'] = ['on','off']
        self.valid_commands['lamp' ]     = ['on','off']
        self.valid_commands['arduino']   = ['duration']
        
        self.device = {}
        self.powersocket = {}
        for idx,dev in enumerate(self.device_list):
            self.powersocket[dev] = idx
            self.device[dev] = None

        self.energenie_lastcommand_date = dt.datetime.utcnow()
        self.energenie_timeout = 10

        self.known_hosts = {}
        self.known_hosts['qubic-central'] = "192.168.2.1"
        self.known_hosts['qubic-studio']  = "192.168.2.8"
        self.known_hosts['calsource']     = "192.168.2.5"
        
        self.broadcast_port = 37020
        self.nbytes = 256
        self.receiver = self.known_hosts['calsource']

        self.energenie = None
        self.hostname = None
        if self.hostname is None and 'HOST' in os.environ.keys():
            self.hostname = os.environ['HOST']
            
        if role is None and self.hostname=='calsource':
            role = 'manager'
        self.role = role
                
        if role=='manager':
            print('I am the calsource configuration manager')
            self.energenie = PMSDevice('energenie', '1')
            self.device['modulator'] = modulator()
            self.device['calsource'] = calibration_source('LF')
            self.device['arduino']   = arduino()
            self.device['arduino'].init()

        # try to get hostname from the ethernet device
        cmd = '/sbin/ifconfig -a'
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = proc.communicate()
        match = re.match('.* inet (192\.168\.2\..*?) ',out.replace('\n',' '))
        if match:
            ip_addr = match.groups()[0]
            self.hostname = ip_addr

        # finally, if still undefined
        if self.hostname is None:
            self.hostname = 'localhost'

        self.log('Calibration Source Configuration: I am %s as the %s' % (self.hostname,self.role))
        return None

    def parse_command_string(self,cmdstr):
        '''
        parse the command string into a command dictionary
        '''

        # the returned command dictionary is a dictionary of dictionaries
        command = {}
        command['timestamp'] = {}
        for dev in self.device_list:
            command[dev] = {}

        command['all'] = {}
        command['all']['status'] = False
        
        command_lst = cmdstr.strip().lower().split()
        tstamp_str = command_lst[0]
        try:
            command['timestamp']['sent'] = eval(tstamp_str)
        except:
            command['timestamp']['sent'] = tstamp_str
        
        command_lst = command_lst[1:]
        dev = 'unknown'
        for cmd in command_lst:
            if cmd=='status':
                command['all']['status'] = True
                continue

            if cmd=='on' or cmd=='off':
                command['all']['onoff'] = cmd
                for dev in ['calsource','amplifier','modulator']:
                    command[dev]['onoff'] = cmd
                continue

            if cmd=='save':
                command['arduino']['save'] = True
                continue
                    
            
            cmd_lst = cmd.split(':')
            try:
                devcmd = cmd_lst[1]
                dev = cmd_lst[0]
            except:
                # if we forget to specify the device, use the most recent one
                devcmd = cmd_lst[0]

            if dev not in self.device_list:
                continue
            
            if devcmd.find('=')>0:
                devcmd_lst = devcmd.split('=')
                parm = devcmd_lst[0]
                val = devcmd_lst[1]

                if parm not in self.valid_commands[dev]:
                    continue
                
                try:
                    command[dev][parm] = eval(val)
                    #print('%s %s = %f (a number)' % (dev,parm,command[dev][parm]))
                except:
                    command[dev][parm] = val
                    #print('%s %s = %s (a string)' % (dev,parm,command[dev][parm]))
                    
            else:
                if devcmd=='on' or devcmd=='off':
                    parm = 'onoff'
                    val = devcmd
                    if devcmd not in self.valid_commands[dev]:
                        continue
                else:
                    parm = devcmd
                    val = True
                    if parm not in self.valid_commands[dev]:
                        continue
                command[dev][parm] = val
        return command


    def listen_for_command(self):
        '''
        listen for a command string arriving on socket
        this message is called by the "manager"
        '''
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        client.bind((self.receiver, self.broadcast_port))

        now = dt.datetime.utcnow()
        self.log('client listening on %s' % self.receiver)

        cmdstr, addr = client.recvfrom(self.nbytes)
        cmdstr_clean = ' '.join(cmdstr.strip().split())
        received_date = dt.datetime.utcnow()
        received_tstamp = eval(received_date.strftime('%s.%f'))
        
        self.log('received a command from %s at %s: %s' % (addr,received_date.strftime(self.date_fmt),cmdstr_clean))
        return received_tstamp, cmdstr_clean, addr[0]

    def listen_for_acknowledgement(self,timeout=None):
        '''
        listen for an acknowledgement string arriving on socket
        this message is called by the "commander" after sending a command
        '''
        if timeout is None: timeout = 25
        if timeout < 25: timeout = 25
        
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        client.settimeout(timeout)
        client.bind((self.hostname, self.broadcast_port))

        now = dt.datetime.utcnow()
        self.log('waiting up to %.0f seconds for acknowledgement on %s' % (timeout,self.hostname))

        try:
            ack, addr = client.recvfrom(self.nbytes)
        except:
            self.log('no response from Calibration Source Manager')
            return None
        received_date = dt.datetime.utcnow()
        received_tstamp = eval(received_date.strftime('%s.%f'))
        self.log('acknowledgement from %s at %s' % (addr,received_date.strftime(self.date_fmt)))
        # clean up the acknowledgement
        ack_cleaned = ''
        for line in ack.strip().split('|'):
            ack_cleaned += '%s\n' % line.strip()
        self.log(ack_cleaned)
        return received_tstamp, ack
    

    def onoff(self,states):
        '''
        switch on or off devices
        we have to wait for the Energenie powerbar to reset
        '''
        reset_delta = self.energenie_timeout # minimum time to wait
        now = dt.datetime.utcnow()
        delta = tot_seconds(now - self.energenie_lastcommand_date)

        if delta < reset_delta:
            extra_wait = reset_delta - delta
            time.sleep(extra_wait)

        try:
            self.energenie.set_socket_states(states)
            ack = 'OK'
        except:
            ack = 'FAILED'


        # check for the amplifier and lamp
        if ack=='OK':
            if 3 in states.keys():
                self.amp_on = states[3]
            if 2 in states.keys():
                self.lamp_on = states[2]
    
        self.energenie_lastcommand_date = dt.datetime.utcnow()
        return ack


    def status(self):
        '''
        return status of all the components
        '''
        msg = ''
        dev = 'amplifier'
        msg += '%s: ' % dev
        if self.amp_on is not None:
            if self.amp_on:
                msg += 'ON'
            else:
                msg += 'OFF'
        else:
            msg += 'UNKNOWN'

        for dev in ['arduino','calsource','modulator']:
            msg += ' | %s: ' % dev
            if self.device[dev].is_connected():
                msg += 'ON'
            else:
                msg += 'OFF'

        dev = 'modulator'
        if self.device[dev].is_connected():
            settings = self.device[dev].read_settings(show=False)
            if settings is None:
                msg += ' | %s: FAILED TO READ SETTINGS' % dev
            else:
                msg += '| %s: SHAPE=%s FREQUENCY=%.6f Hz AMPLITUDE=%.6f V OFFSET=%.6f V DUTY CYCLE=%.1f%%' % \
                    (dev,
                     settings['shape'],
                     settings['frequency'],
                     settings['amplitude'],
                     settings['offset'],
                     settings['duty'])
        
            
        return msg
    
    def interpret_commands(self,command,retval):
        '''
        interpret the dictionary of commands, and take the necessary steps
        this method is called by the "manager"
        '''

        ack = '%s' % dt.datetime.utcnow().strftime('%s.%f')

        # add None to modulator parameters that are to be set by default
        modulator_configure = False
        for parm in ['frequency','amplitude','shape','offset','duty']:
            if parm in command['modulator'].keys():
                modulator_configure = True
            else:
                command['modulator'][parm] = None
                

        # do all on/off commands first
        parm = 'onoff'
        states = {}
        msg = ''
        devlist = command.keys()
        devlist.remove('all')
        devlist.remove('timestamp')
        for dev in devlist:
            if parm in command[dev].keys():
                state = None
                if command[dev][parm] == 'on':
                    state = True
                if command[dev][parm] == 'off':
                    state = False
                if state is not None:
                    states[self.powersocket[dev]] = state
                    msg += 'switch %s %s: ' % (command[dev][parm],dev)
        if states:
            msg += 'power on/off command %s' % self.onoff(states)
            self.log(msg)
            ack += ' | %s' % msg
            # wait before doing other stuff
            time.sleep(3)

            # initialize devices that need initializing
            for dev in ['modulator','calsource']:
                powersocket = self.powersocket[dev]
                if powersocket in states.keys() and states[powersocket]:
                    self.device[dev].set_default_settings()

        # do configuration command for calsource
        dev = 'calsource'
        parm =  'frequency'
        if dev in command.keys() and parm in command[dev].keys():
            of = self.device[dev].set_Frequency(command[dev][parm])
            msg = '%s:%s=%.1f: ' % (dev,parm,command[dev][parm])
            if of is None:
                msg += 'FAILED'
            else:
                msg += 'OK.  synthesiser frequency=%.6fGHz' % of
            self.log(msg)
            ack += ' | %s' % msg
                

        # the modulator configuration
        dev = 'modulator'
        if dev in command.keys() and modulator_configure:
            self.device[dev].configure(frequency=command[dev]['frequency'],
                                       amplitude=command[dev]['amplitude'],
                                       shape=command[dev]['shape'],
                                       offset=command[dev]['offset'],
                                       duty=command[dev]['duty'])

            # wait a bit before trying to read the results
            time.sleep(1)
            settings = self.device[dev].read_settings(show=False)
            if settings is None:
                msg = '%s: COMMAND FAILED' % dev
            else:
                msg = '%s: SHAPE=%s FREQUENCY=%.6f Hz AMPLITUDE=%.6f V OFFSET=%.6f V DUTY CYCLE=%.1f%%' % \
                    (dev,
                     settings['shape'],
                     settings['frequency'],
                     settings['amplitude'],
                     settings['offset'],
                     settings['duty'])
                    
            self.log(msg)
            ack += ' | %s' % msg


        # run the Arduino last of all
        dev = 'arduino'
        if dev in command.keys():
            if 'duration' in command[dev].keys():
                filename = self.device[dev].acquire(command[dev]['duration'],True)
                if filename is None:
                    ack += ' | Arduino acquistion failed'
                else:
                    ack += ' | Arduino data saved to file: %s' % filename

            if 'save' in command[dev].keys():
                self.device[dev].interrupt()

        # STATUS
        if command['all']['status']:
            ack += ' | %s' % self.status()
            

        retval.append(ack)
        return retval


    def listen_loop(self):
        '''
        keep listening on the socket for commands
        '''
        cmdstr = None
        keepgoing = True
        while keepgoing:
            if cmdstr is None: received_tstamp, cmdstr, addr = self.listen_for_command()
            received_date = dt.datetime.fromtimestamp(received_tstamp)
            command = self.parse_command_string(cmdstr)
            sent_date = dt.datetime.fromtimestamp(command['timestamp']['sent'])
            self.log('command sent:     %s' % sent_date.strftime(self.date_fmt))
            self.log('command received: %s' % received_date.strftime(self.date_fmt))

            # interpret the commands in a separate process and continue listening
            manager = multiprocessing.Manager()
            retval = manager.list()
            proc = multiprocessing.Process(target=self.interpret_commands, args=(command,retval))
            proc.start()
            if 'arduino' in command.keys() and 'duration' in command['arduino'].keys():
                delta = dt.timedelta(seconds=command['arduino']['duration'])
                now = dt.datetime.utcnow()
                stoptime = now + delta
                self.send_acknowledgement('Send command "save" to interrupt and save immediately',addr)
                working = True
                print("going into loop until %s or until 'save' command received" % stoptime.strftime('%Y-%m-%d %H:%M:%S UT'))
                while working and now<stoptime:
                    received_tstamp, cmdstr, addr = self.listen_for_command()
                    now = dt.datetime.utcnow()
                    command2 = self.parse_command_string(cmdstr)
                    if 'arduino' in command2.keys() and 'save' in command2['arduino'].keys():
                        self.device['arduino'].interrupt()
                        working = False
                        cmdstr = None
                    elif now<stoptime:
                        self.send_acknowledgement("I'm busy and can only respond to the 'save' command",addr)
                    else:
                        print('command will be carried into main loop: %s' % cmdstr)
            else:
                cmdstr = None

            proc.join()
            if len(retval)==0:
                ack = 'no acknowledgement'
            else:
                ack = retval[0]
            self.send_acknowledgement(ack,addr)

            
        return
                
    def send_command(self,cmd_str):
        '''
        send commands to the calibration source manager
        '''
        s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.settimeout(0.2)
        s.bind((self.hostname,self.broadcast_port))

        now=dt.datetime.utcnow()
        now_str = now.strftime('%s.%f')
        len_nowstr = len(now_str)
        len_remain = self.nbytes - len_nowstr - 1
        fmt = '%%%is %%%is' % (len_nowstr,len_remain)
        msg = fmt % (now_str,cmd_str)
        #self.log('sending socket data: %s' % msg)

        s.sendto(msg, (self.receiver, self.broadcast_port))
        s.close()
        return

    def send_acknowledgement(self,ack,addr):
        '''
        send an acknowledgement to the commander
        '''
        s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.settimeout(0.2)
        s.bind((self.hostname,self.broadcast_port))

        now=dt.datetime.utcnow()
        now_str = now.strftime('%s.%f')
        len_nowstr = len(now_str)
        len_remain = self.nbytes - len_nowstr - 3
        fmt = '%%%is | %%%is' % (len_nowstr,len_remain)
        msg = fmt % (now_str,ack)
        print('sending acknowledgement: %s' % msg)
        s.sendto(msg, (addr, self.broadcast_port))
        s.close()
        return
    
    def command_loop(self):
        '''
        command line interface to send commands
        '''
        keepgoing = True
        while keepgoing:
            ans=raw_input('Enter command ("help" for list): ')
            cmd_str = ans.strip().lower()
            cmd_list = cmd_str.split()
            if 'help' in cmd_list or 'h' in cmd_list:
                self.command_help()
                continue

            if 'quit' in cmd_list or 'q' in cmd_list:
                keepgoing = False
                continue

            self.send_command(cmd_str)

            # check if we're doing an acquisition or other things that require extra time
            duration = 0
            for cmd in cmd_list:
                if cmd.find('arduino:duration=')==0:
                    duration_str = cmd.split('=')[1]
                    try:
                        duration += eval(duration_str)
                    except:
                        self.log('Could not interpret Arduino duration')
                    continue

                if cmd.find('on')>0 or cmd.find('off')>0:
                    duration += self.energenie_timeout
                    

            # add margin to the acknowledgement timeout
            duration += 5
            response = self.listen_for_acknowledgement(timeout=duration)
                
        return
                
