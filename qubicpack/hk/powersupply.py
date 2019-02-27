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
import datetime as dt
import re
import readline
readline.parse_and_bind('tab: complete')
readline.parse_and_bind('set editing-mode vi')


class PowerSupply :

    def __init__(self,port=None):
        '''initialize an instance of PowerSupply
        '''
        self.port=None
        self.nsupplies=0
        self.info=None
        self.device_ok=False

        if port is None:
            print('NOTE: Please give a device (e.g. port="/dev/ttyACM0")')
            return None

        self.log('PowerSupply to be initiated with port=%s' % port)
        self.init_TTiPowerSupply(port=port)
        return None

    def log(self,msg):
        '''messages to log file and to screen
        '''

        if 'HOME' in os.environ.keys():
            homedir = os.environ['HOME']
        else:
            homedir = '/tmp'
        
        logfile = homedir + os.sep + 'hk_powersupply.log'
        
        now=dt.datetime.utcnow()
        logmsg='%s | %s' % (now.strftime('%Y-%m-%d %H:%M:%S UT'),msg)
        try:
            h=open(logfile,'a')
            h.write(logmsg+'\n')
            h.close()
        except:
            pass
        print(logmsg)
        return
                
    def identify_PowerSupply(self):
        '''identify the power supply
        '''

        if self.port is None:
            self.log('ERROR! Please give a device to identify (e.g. /dev/ttyACM0)')
            self.device_ok=False
            return  None
        
        # find out which power supply it is, and whether it has one or two supplies
        cmd='/sbin/udevadm info -a %s|grep serial|head -1' % self.port
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out,err=proc.communicate()
        serialno=out.split('==')[1].replace('"','').strip()

        s=serial.Serial(port=self.port)
        s.write('*IDN?\n')
        a=s.readline()
        a_list=a.strip().split(',')
        if len(a_list)<2:
            self.log('ERROR! This does not appear to be a TTi Power Supply')
            self.device_ok=False
            return None

        supplyname=a_list[1].strip()
        info={}
        info['port']=self.port
        info['serialno']=serialno
        info['id_string']=a.strip()
        info['supplyname']=supplyname
        info['nsupplies']=self.get_nsupplies()
        info['label_left']='Left'
        info['label_right']='Right'

        # check if this is a known supply
        serialnos=list(known_supplies.serial_number)
        idx=None
        if serialno in serialnos:
            idx = serialnos.index(serialno)
            label = known_supplies[idx].label
            info['label_left']=known_supplies[idx].label_left
            info['label_right']=known_supplies[idx].label_right
        
        self.info=info
        self.read_userlabels()
        self.supplyname=supplyname
        self.serialno=serialno
        self.device_ok=True
        self.log('%s on port %s is okay' % (supplyname,self.port))
        return info

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

    def read_userlabels(self):
        ''' read user supplied labels corresponding to HEATER1, HEATER2, etc
            this is called by identify_PowerSupply()
        '''
        if 'HOME' in os.environ.keys():
            homedir = os.environ['HOME']
        else:
            homedir = os.path.curdir
        
        configfile = homedir + os.sep + 'powersupply.conf'
        if not os.path.isfile(configfile):
            return
        
        h = open(configfile,'r')
        lines = h.read().split('\n')
        for line in lines:
            match = re.match('^(HEATER.*): (.*)',line)
            if match:
                label = match.groups()[0]
                userlabel = match.groups()[1]
                if label==self.info['label_left']:
                    self.info['userlabel_left']=userlabel
                    continue
                if label==self.info['label_right']:
                    self.info['userlabel_right']=userlabel
                    continue
            
        return
    
    def init_TTiPowerSupply(self,port=None):
        '''initialize the power supply
        it should be recognized as /dev/powersupply or /dev/ttyACMn (n=0,1,2,...)
        
        it is usable by everyone because the following is in udev rules:

        SUBSYSTEM=="tty", ATTRS{idVendor}=="103e", ATTRS{idProduct}=="0424", OWNER="pi",
        GROUP="users", MODE="0666", SYMLINK+="powersupply"
        '''

        errmsg=None
        if port is None:
            errmsg='ERROR! No Device specified.'
        elif not os.path.exists(port):
            errmsg='ERROR! Device does not exist.'

        if errmsg is not None:
            self.log(errmsg)
            self.port=None
            self.nsupplies=0
            self.supplyname=None
            self.device_ok=False
            return None
        
        self.port=port

        s=serial.Serial(port=port,timeout=0.1)
        self.s=s

        info=self.identify_PowerSupply()
        return info

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
            self.log('ERROR! Unknown power supply: %s' % supply)
            self.log('Please tell me if its "left" or "right" or "1" or "2"')
            return None

        return supplyno

    def send_Command(self,cmd,supply='left'):
        '''send a command to the power supply
        '''
        supplyno=self.supplyno(supply)
        if supplyno is None:return False

        if supplyno>self.nsupplies:
            self.log('ERROR! This power supply does not have that many supplies: %s, S# %s, on port %s'\
                     % (self.info['supplyname'],self.info['serialno'],self.info['port']))
            return False
        cmd=cmd % supplyno

        try:
            response=self.s.write(cmd)
        except:
            self.log('ERROR! Could not write command to powersupply: %s, %s, id# %s' % (self.port,self.supplyname,self.serialno))
            self.device_ok = False
            return False
        
        if response>0:return True
        return False

    def read_reply(self):
        '''read the reply from the power supply
        Note that some commands do not send a reply
        Trying to read after a command which does not send a reply
        will cause hanging
        '''
        try:
            ans=self.s.readline()
        except:
            ans=None
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

    def getReadings(self,supply='left'):
        '''get the Voltage and Current readings given a label
        '''
        V=self.get_VoltageSetting(supply)
        I=self.get_CurrentOutput(supply)
        Status=self.OutputStatus(supply)
        return (V,I,Status)

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
        subttl_left  = self.info['label_left']
        subttl_right = self.info['label_right']
        if 'userlabel_left' in self.info.keys():
            subttl_left += ': %s' % self.info['userlabel_left']
        if 'userlabel_right' in self.info.keys():
            subttl_right += ': %s' % self.info['userlabel_right']

        print(ttl)
        if self.nsupplies==2:
            Vleft=self.get_VoltageSetting('left')
            Ileft=self.get_CurrentOutput('left')
            StatusLeft=self.OutputStatus('left')
            print(subttl_left)
            try:
                print('   Voltage: %f V\n   Current: %f mA\n   Output: %s\n' % (Vleft,Ileft,StatusLeft))
            except:
                print('   Voltage: %s V\n   Current: %s mA\n   Output: %s\n' % (Vleft,Ileft,StatusLeft))
                
        print(subttl_right+'\n')
        Vright=self.get_VoltageSetting('right')
        Iright=self.get_CurrentOutput('right')
        StatusRight=self.OutputStatus('right')
        try:
            print('   Voltage: %f V\n   Current: %f mA\n   Output: %s\n' % (Vright,Iright,StatusRight))
        except:
            print('   Voltage: %s V\n   Current: %s mA\n   Output: %s\n' % (Vright,Iright,StatusRight))
            
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

            if parms['readings']:
                return self.getReadings(subsupply)
            
        return self.Status()
# end of Class definition PowerSupply()


class PowerSupplies :
    '''a class to manage multiple power supplies
    '''

    def __init__(self):
        self.supplylist=None
        self.infolist=None
        self.serialno_list=None
        self.nsupplies=None
        self.find_PowerSupply()
        return None

    
    def find_PowerSupply(self):
        '''find devices
        '''
        
        devs1=glob('/dev/ttyACM*')
        #devs2=glob('/dev/ttyUSB*') # these are not TTi power supplies
        devs=devs1
        if not devs:
            self.log('No power supplies found!')
            return None

        devs.sort()
        supplylist=[]
        infolist=[]
        serialno_list=[]
        userlabel_left_list = []
        userlabel_right_list = []
        for dev in devs:
            p=PowerSupply(dev)
            if p.device_ok:
                supplylist.append(p)
                infolist.append(p.info)
                serialno_list.append(p.info['serialno'])
                if 'userlabel_left' in p.info.keys():
                    userlabel_left_list.append(p.info['userlabel_left'])
                else:
                    userlabel_left_list.append(p.info['label_left'])
                if 'userlabel_right' in p.info.keys():
                    userlabel_right_list.append(p.info['userlabel_right'])
                else:
                    userlabel_right_list.append(p.info['label_right'])
                    

        self.nsupplies=len(supplylist)
        self.infolist=infolist
        self.serialno_list=serialno_list
        self.supplylist=supplylist
        self.userlabel_left_list=userlabel_left_list
        self.userlabel_right_list=userlabel_right_list
        return 

    def parseargs(self,argv):
        '''parse the command line arguments 
        and return a dictionary with the interpreted commands
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
        command['readings']=False
    
        supplylist=list(known_supplies.supplyname)
        supplylabels=list(known_supplies.label)
        supplylabels_left=list(known_supplies.label_left)
        supplylabels_right=list(known_supplies.label_right)
        serialnos=list(known_supplies.serial_number)
    
        for arg in argv:
            arg=arg.strip()
            a=arg.upper()
            if a.find('V=')==0:
                try:
                    V=eval(a.split('=')[1])
                    command['V']=V
                except:
                    self.log('Could not read voltage value: %s' % arg)
                continue
        
            if a=='ON':
                command['ONOFF']=1
                continue

            if a=='OFF':
                command['ONOFF']=0
                continue

            if arg in self.userlabel_left_list:
                idx=self.userlabel_left_list.index(arg)
                command['serialno']=self.supplylist[idx].info['serialno']
                command['subsupply']='LEFT'
                continue

            if arg in self.userlabel_right_list:
                idx=self.userlabel_right_list.index(arg)
                command['serialno']=self.supplylist[idx].info['serialno']
                command['subsupply']='RIGHT'
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
            
            if a.find('READINGS')>=0:
                command['readings']=True
                continue

            if a=='--TEST':
                command['test']=True

        return command

    def runCommands(self,command,quiet=True):
        '''run the commands on the requested power supply
        the argument is a dictionary returned from parseargs()
        '''
        known_serialnos=list(known_supplies.serial_number)
        serialnos=self.serialno_list
        ret=None
        if command['serialno'] in serialnos:
            idx=serialnos.index(command['serialno'])
            label=''
            if command['serialno'] in known_serialnos:
                known_idx=known_serialnos.index(command['serialno'])
                label=list(known_supplies.label)[known_idx]
            if not quiet: self.log('applying commands on supply %s: %s' % (self.supplylist[idx].supplyname,label))
            p=self.supplylist[idx]
            ret=p.runCommands(command)
        
        return ret
    
    def help_PowerSupply(self):
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
                   'HEATER1',
                   'HEATER2')

known_supplies[1]=('D5E586A0',
                   '423393',
                   'PLH120-P',
                   'THURLBY THANDAR, PLH120-P,  423393, 1.01 - 3.13',
                   1,
                   'PLH120-P',
                   '',
                   'HEATER3')

known_supplies[2]=('435297',
                   '435297',
                   'PL303-P',
                   'THURLBY THANDAR, PL303-P, 435297, 3.02-4.01',
                   1,
                   'PL303-P',
                   'None',
                   'HEATER4')

known_supplies[3]=('504183',
                   '504183',
                   'PL303QMD-P',
                   'THURLBY THANDAR, PL303QMD-P, 504183, 3.05-4.06',
                   2,
                   'PL303QMD-P_2',
                   'HEATER5',
                   'HEATER6')

known_supplies[4]=('ftCYWB2W',
                   '',
                   'Agilent 34401A',
                   '',
                   0,
                   'Voltmeter',
                   '',
                   '')



if __name__=='__main__':

    ps=PowerSupplies()
    command=ps.parseargs(sys.argv)
    keep_going=not command['quit']
    while keep_going:
        ps.runCommands(command)

        for p in ps.supplylist:
            p.Status()
        
        if command['help']:
            ps.help_PowerSupply()
            print('Available Power Supplies')
            for info in ps.infolist:
                print('%s' % info['supplyname'])

        ans=raw_input('Enter command ("help" for list): ')
        command=ps.parseargs(ans.split())
        keep_going=not command['quit']
        
    
