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
import socket,subprocess,time
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
        txt += '    valid devices: %s\n' % device_list_str
        for dev in self.device_list:
            valid_commands = ', '.join(self.valid_commands[dev])
            txt += 'valid commands for %s: %s\n' % (dev,valid_commands)
        txt += 'Example:\n'
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
            
        self.qubic_central = "192.168.2.1"
        self.qubic_studio  = "192.168.2.8"
        self.raspberrypi   = "192.168.2.5"
        
        self.broadcast_port = 37020
        self.nbytes = 256
        self.receiver = self.raspberrypi

        self.energenie = None
        self.hostname = None
        if role is None:
            # try to get the role from the hostname
            if 'HOST' in os.environ.keys():
                self.hostname = os.environ['HOST']
            if self.hostname=='calsource':
                role = 'manager'
        self.role = role
                
        if role=='manager':
            print('I am the calsource configuration manager')
            self.energenie = PMSDevice('energenie', '1')
            self.device['modulator'] = modulator()
            self.device['calsource'] = calibration_source('LF')

        # if undefined, try to get hostname from the ethernet device
        if self.hostname is None:
            cmd = 'ifconfig -a'
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            out, err = proc.communicate()
            lines = out.split('\n')
            for idx,line in enumerate(lines):
                if line.find('eth')==0:
                    idx_addr = idx + 1
                    if idx_addr < len(lines):
                        self.hostname = lines[idx_addr].split()[1].strip()
                    break

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

        command_lst = cmdstr.strip().split()
        tstamp_str = command_lst[0]
        try:
            command['timestamp']['sent'] = eval(tstamp_str)
        except:
            command['timestamp']['sent'] = tstamp_str

        
        command_lst = command_lst[1:]
        dev = 'unknown'
        for cmd in command_lst:
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
        received_date = dt.datetime.utcnow()
        received_tstamp = eval(received_date.strftime('%s.%f'))
        self.log('received a command from %s at %s' % (addr,received_date.strftime(self.date_fmt)))
        return received_tstamp, cmdstr, addr[0]

    def listen_for_acknowledgement(self):
        '''
        listen for an acknowledgement string arriving on socket
        this message is called by the "commander" after sending a command
        '''
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        client.settimeout(25)
        client.bind((self.hostname, self.broadcast_port))

        now = dt.datetime.utcnow()
        self.log('listening for acknowledgement on %s' % self.hostname)

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
    

    def interpret_commands(self,command):
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
                

        for dev in command.keys():

            # check for on/off commands
            for parm in command[dev].keys():
                if parm=='onoff':
                    state = None
                    if command[dev][parm] == 'on':
                        state = True
                    if command[dev][parm] == 'off':
                        state = False
                    if state is not None:
                        msg = 'switch %s %s: ' % (command[dev][parm],dev)
                        try:
                            self.energenie.set_socket_states({self.powersocket[dev]:state})
                            time.sleep(4) # wait a bit after switching off/on
                            msg += 'OK'                        
                        except:
                            msg += 'FAILED'
                        ack += ' | %s' % msg
                        self.log(msg)
                    continue
                
                if dev=='calsource' and parm=='frequency':
                    of = self.device[dev].set_Frequency(command[dev][parm])
                    msg = '%s:%s=%.1f: ' % (dev,parm,command[dev][parm])
                    if of is None:
                        msg += 'FAILED'
                    else:
                        msg += 'OK.  synthesiser frequency=%.2fGHz' % of
                    self.log(msg)
                    ack += ' | %s' % msg
                    continue

            # handle the modulator separately
            if dev=='modulator' and modulator_configure:
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
                    msg = '%s: SHAPE=%s FREQUENCY=%.2f Hz AMPLITUDE=%.3f V OFFSET=%.3f V DUTY CYCLE=%.1f%%' % \
                        (dev,settings['shape'],
                         settings['frequency'],
                         settings['amplitude'],
                         settings['offset'],
                         settings['duty'])
                    
                self.log(msg)
                ack += ' | %s' % msg
                
        return ack


    def listen_loop(self):
        '''
        keep listening on the socket for commands
        '''
        keepgoing = True
        while keepgoing:
            received_tstamp, cmdstr, addr = self.listen_for_command()
            received_date = dt.datetime.fromtimestamp(received_tstamp)
            command = self.parse_command_string(cmdstr)
            sent_date = dt.datetime.fromtimestamp(command['timestamp']['sent'])
            self.log('command sent:     %s' % sent_date.strftime(self.date_fmt))
            self.log('command received: %s' % received_date.strftime(self.date_fmt))
            
            ack = self.interpret_commands(command)
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
            if cmd_str.find('help')>=0:
                self.command_help()
                continue

            if cmd_str.find('quit')>=0:
                keepgoing = False
                continue

            if cmd_str == 'q':
                keepgoing = False
                continue

            self.send_command(cmd_str)
            response = self.listen_for_acknowledgement()
                
        return
                
