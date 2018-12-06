#!/usr/bin/env python
'''
$Id: powersupply.py
$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
$created: Fri 23 Nov 2018 11:25:22 CET
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

control the TTi PLxxx power supply via USB

The TTi PL303QMD-P power supply has two supplies
  1) on the right hand side
  2) on the left hand side

'''
from __future__ import division, print_function
import os,sys,serial,subprocess
from glob import glob
import numpy as np

import readline
readline.parse_and_bind('tab: complete')
readline.parse_and_bind('set editing-mode vi')


class PowerSupply :

    def __init__(self,port=None):
        '''initialize an instance of PowerSupply
        '''
        self.port=None
        self.available_supplies=None
        self.nsupplies=0

        if port is None:
            available_supplies=find_PowerSupply()
            print('\nNOTE: Please choose a supply, and run init_TTIPowerSupply(dev)')
            return None

        self.init_TTiPowerSupply(port=port)
        return None


    def get_nsupplies(self):
        '''get the number of supplies
        '''
        self.s.write('CONFIG?\n')
        a=self.read_reply()
        try:
            nsupplies=eval(a)
        except:
            nsupplies=1
        self.nsupplies=nsupplies
        return nsupplies
    
    def init_TTiPowerSupply(self,port='/dev/powersupply'):
        '''initialize the power supply
        it should be recognized as /dev/powersupply or /dev/ttyACMn (n=0,1,2,...)
        
        it is usable by everyone because the following is in udev rules:

        SUBSYSTEM=="tty", ATTRS{idVendor}=="103e", ATTRS{idProduct}=="0424", OWNER="pi",
        GROUP="users", MODE="0666", SYMLINK+="powersupply"
        '''
        if not os.path.exists(port):
            print('ERROR! Device does not exist.')
            self.port=None
            self.nsupplies=0
            self.supplyname=None
            return None
        self.port=port

        s=serial.Serial(port=port)
        self.s=s

        self.s.write('*IDN?\n')
        a=self.read_reply()
        a_list=a.split(',')
        #self.supplyname='%s %s' % (a_list[0],a_list[1])
        self.supplyname=a_list[1].strip()
        nsupplies=self.get_nsupplies()
        info=identify_PowerSupply(port)
        self.serialno=info['serialno']
        #print('%8s: %s' % (self.serialno,self.supplyname))
        return a

    def supplyno(self,supply):
        ''' convert a name given as a string to the corresponding number
        '''
        supplyno=-1
        if isinstance(supply,str):
            ans=supply.strip().lower()
            if ans=='left' or ans=='2':supplyno=2
            if ans=='right' or ans=='1':supplyno=1

        if isinstance(supply,int):
            supplyno=supply

        if supplyno not in [1,2]:
            print('ERROR! Unknown power supply: %s' % supply)
            print('Please tell me if its "left" or "right" or "1" or "2"')
            return None

        return supplyno

    def send_Command(self,cmd,supply='left'):
        '''send a command to the power supply
        '''
        supplyno=self.supplyno(supply)
        if supplyno is None:return False

        if supplyno>self.nsupplies:
            print('ERROR! This power supply does not have that many supplies')
            return False
        cmd=cmd % supplyno
        
        response=self.s.write(cmd)
        if response>0:return True
        return False

    def read_reply(self):
        '''read the reply from the power supply
        Note that some commands do not send a reply
        Trying to read after a command which does not send a reply
        will cause hanging
        '''
        ans=self.s.readline()
        return ans
        
    def set_Voltage(self,V,supply='left'):
        '''set the voltage
        '''
        cmd='V%%i %f\n' % V
        return self.send_Command(cmd,supply)


    def get_VoltageSetting(self,supply='left'):
        '''get the current setting of the voltage supply
        Note that this is not necessarily the actual voltage supplied
        '''
        cmd='V%i?\n'
        result=self.send_Command(cmd,supply)
        if result:
            ans=self.read_reply()
            try:
                val=eval(ans.strip().split()[1])
            except:
                val=ans
            return val
        return result

    def get_CurrentOutput(self,supply='left'):
        '''get the current supplied
        '''
        cmd='I%iO?\n'
        result=self.send_Command(cmd,supply)
        if result:
            ans=self.read_reply()
            try:
                val=eval(ans.strip().replace('A',''))
                val*=1e3
            except:
                val=ans
            return val
        return result

    def OutputOn(self,supply='left'):
        '''enable the output
        '''
        cmd='OP%i 1\n'
        return self.send_Command(cmd,supply)

    def OutputOff(self,supply='left'):
        '''disable the output
        '''
        cmd='OP%i 0\n'
        return self.send_Command(cmd,supply)

    def OutputStatus(self,supply='left'):
        '''get the output status (on/off)
        '''
        status='unknown'
        cmd='OP%i?\n'
        result=self.send_Command(cmd,supply)
        if result:
            ans=self.read_reply()
            try:
                val=eval(ans.strip())
            except:
                val=ans
                status=ans
            if val==0:status='OFF'
            if val==1:status='ON'
            return status
        return status
        

    def Status(self):
        '''print out all the parameters of both power supplies
        '''

        ttl='\nPower Supply: '+self.supplyname
        subttl_left='"Left" supply'
        subttl_right='"Right" supply'
        serialnos=list(known_supplies.serial_number)
        idx=None
        if self.serialno in serialnos:
            idx=serialnos.index(self.serialno)
            ttl='\nPower Supply: %s' % known_supplies[idx].label
            subttl_left=known_supplies[idx].label_left
            subttl_right=known_supplies[idx].label_right

        print(ttl)
        if self.nsupplies==2:
            Vleft=self.get_VoltageSetting('left')
            Ileft=self.get_CurrentOutput('left')
            StatusLeft=self.OutputStatus('left')
            print(subttl_left)
            print('   Voltage: %f V\n   Current: %f mA\n   Output: %s\n' % (Vleft,Ileft,StatusLeft))
            
        print(subttl_right+'\n')
        Vright=self.get_VoltageSetting('right')
        Iright=self.get_CurrentOutput('right')
        StatusRight=self.OutputStatus('right')
        print('   Voltage: %f V\n   Current: %f mA\n   Output: %s\n' % (Vright,Iright,StatusRight))
        
        return


    def runCommands(self,parms):
        '''execute requested commands
        '''
        subsupply=None
        if 'subsupply' in parms.keys():
            subsupply=parms['subsupply']

        if 'V' in parms.keys():
            V=parms['V']

        if 'ONOFF' in parms.keys():
            ONOFF=parms['ONOFF']

        if subsupply is None and self.nsupplies==1:
            subsupply=1

        if not subsupply is None:
            if V is not None:
                self.set_Voltage(V,subsupply)

            if ONOFF is not None:
                if ONOFF==1:
                    self.OutputOn(subsupply)
                elif ONOFF==0:
                    self.OutputOff(subsupply)

        return self.Status()
# end of Class definition PowerSupply()


def find_PowerSupply():
    '''find devices
    '''
    available_supplies=[]
    devs1=glob('/dev/ttyACM*')
    devs2=glob(' /dev/ttyUSB*')
    devs=devs1+devs2
    if not devs:
        print('No power supplies found!')
        return None

    available_supplies=[]
    for dev in devs:
        info=identify_PowerSupply(dev)
        available_supplies.append(info)
    
    return available_supplies        

def identify_PowerSupply(port=None):
    '''identify the power supply
    '''

    if port is None:
        print('ERROR! Please give a device to identify (e.g. /dev/ttyACM0)')
        return  None
        
    # find out which power supply it is, and whether it has one or two supplies
    cmd='/sbin/udevadm info -a %s|grep serial|head -1' % port
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out,err=proc.communicate()
    serialno=out.split('==')[1].replace('"','').strip()

    s=serial.Serial(port=port)
    s.write('*IDN?\n')
    a=s.readline()
    a_list=a.split(',')
    supplyname=a_list[1].strip()

    info={}
    info['port']=port
    info['serialno']=serialno
    info['id_string']=a.strip()
    info['supplyname']=supplyname
    return info

def parseargs_PowerSupply(argv):
    '''parse the command line arguments
    '''
    command={}
    command['ONOFF']=None
    command['supplyname']=None
    command['label']=None
    command['serialno']=None
    command['subsupply']=None
    command['V']=None
    command['quit']=False
    command['help']=False
    command['status']=False
    
    supplylist=list(known_supplies.supplyname)
    supplylabels=list(known_supplies.label)
    supplylabels_left=list(known_supplies.label_left)
    supplylabels_right=list(known_supplies.label_right)
    
    for arg in argv:
        arg=arg.strip()
        a=arg.upper()
        if a.find('V=')==0:
            try:
                V=eval(a.split('=')[1])
                command['V']=V
            except:
                print('Could not read voltage value: %s' % arg)
            continue
        
        if a=='ON':
            command['ONOFF']=1
            continue

        if a=='OFF':
            command['ONOFF']=0
            continue
            
        if arg in supplylabels_left:
            idx=supplylabels_left.index(arg)
            command['subsupply']='LEFT'
            command['label']=supplylabels[idx]
            command['serialno']=serialnos[idx]
            continue

        if arg in supplylabels_right:
            idx=supplylabels_right.index(arg)
            command['subsupply']='RIGHT'
            command['label']=supplylabels[idx]
            command['serialno']=serialnos[idx]
            continue

        if arg in supplylabels:
            idx=supplylabels.index(arg)
            command['label']=arg
            command['serialno']=serialnos[idx]
            continue

        if a in ['LEFT','RIGHT']:
            command['subsupply']=a
            continue

        if arg in supplylist:
            idx=supplylist.index(arg)
            command['supplyname']=arg
            command['serialno']=serialnos[idx]
            continue

        if a=='QUIT' or a=='Q':
            command['quit']=True
            continue

        if a.find('HELP')>=0:
            command['help']=True
            continue

        if a.find('STATUS')>=0:
            commmand['status']=True
            continue

        if a=='--TEST':
            command['test']=True

    return command


def help_PowerSupply():
    '''some help text for command power supplies
    '''
    msg='\nPower Supply Control/Command\n'
    msg+='\ncommands:\n'
    msg+='\nhelp : print this message'
    msg+='\n<return> : show status of all power supplies (default action)'
    msg+='\n<supply name> : apply commands to this power supply'
    msg+='\n<left|right> : for power supplies with two supplies, apply command to the left or right supply'
    msg+='\n<label> : apply commands to the supply with this label (eg. "heater 1K")'
    msg+='\n<on|off> : switch output on or off'
    msg+='\nV=<num> : set voltage to <num>\n'
    print(msg)
    return

# Known Power Supplies
# The serial numbers of known power supplies, and how many ports they have        
fmts_headings=['serial_number','id_number','supplyname','id_string','nsupplies','label','label_left','label_right']
fmts=['a8','a6','a16','a60','i1','a20','a20','a20']
known_supplies=np.recarray(formats=fmts,names=fmts_headings,shape=(5))
known_supplies[0]=('D5E588EA',
                   '426040',
                   'PL303QMD-P',
                   'THURLBY THANDAR, PL303QMD-P,  426040, 3.02 - 3.13',
                   2,
                   'PL303QMD-P_1',
                   'Heater L',
                   'Heater R')

known_supplies[1]=('D5E586A0',
                   '423393',
                   'PLH120-P',
                   'THURLBY THANDAR, PLH120-P,  423393, 1.01 - 3.13',
                   1,
                   'PLH120-P',
                   '',
                   'Undefined Heater Location')

known_supplies[2]=('435297',
                   '435297',
                   'PL303-P',
                   'THURLBY THANDAR, PL303-P, 435297, 3.02-4.01',
                   1,
                   'PL303-P',
                   'None',
                   'Right')

known_supplies[3]=('504183',
                   '504183',
                   'PL303QMD-P',
                   'THURLBY THANDAR, PL303QMD-P, 504183, 3.05-4.06',
                   2,
                   'PL303QMD-P_2',
                   'Heater L',
                   'Heater R')

known_supplies[4]=('ftCYWB2W',
                   '',
                   'Agilent 34401A',
                   '',
                   0,
                   'Voltmeter',
                   '',
                   '')
                
if __name__=='__main__':

    available_supplies=find_PowerSupply()
    if available_supplies is None:
        available_supplies=[]
    nsupplies=len(available_supplies)
    supply=[]
    available_models=[]
    labels=[]
    serialnos=[]
    known_serialnos=list(known_supplies.serial_number)
    
    command=parseargs_PowerSupply(sys.argv)

    for info in available_supplies:
        print(info['supplyname'])
        dev=info['port']
        p=PowerSupply(dev)
        supply.append(p)
        available_models.append(info['supplyname'])
        serialnos.append(info['serialno'])

    keep_going=not command['quit']
    while keep_going:
        if command['serialno'] in serialnos:
            idx=serialnos.index(command['serialno'])
            label=''
            if command['serialno'] in known_serialnos:
                known_idx=known_serialnos.index(command['serialno'])
                label=list(known_supplies.label)[known_idx]
            print('applying commands on supply %s: %s' % (available_models[idx],label))
            p=supply[idx]
            p.runCommands(command)
        

        for p in supply:
            p.Status()
        
        if command['help']:
            help_PowerSupply()
            print('Available Power Supplies')
            for model in available_models:
                print('%s' % model)

        ans=raw_input('Enter command ("help" for list): ')
        command=parseargs_PowerSupply(ans.split())
        keep_going=not command['quit']
        
    
