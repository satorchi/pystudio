#!/usr/bin/env python
'''
$Id: qubic_bot.py
$auth: Manuel Gonzalez <manuel.gonzalez@ib.edu.ar>
$created: Tues 12 June 2018

$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

This is the QUBIC Telegram bot
https://web.telegram.org/#/im?p=@QUBIC_bot

'''
from __future__ import division, print_function
import sys,os,re,time,subprocess,inspect
import datetime as dt
from glob import glob
import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

from satorchipy.datefunctions import str2dt

class dummy_bot:
    '''
    a dummy bot for testing
    '''
    def __init__(self):
        return

    def sendMessage(self,chat_id,answer):
        print('TESTMODE: Bot sent:\n  %s' % answer)
        return

    def sendPhoto(self,chat_id,photo):
        print('TESTMODE: Bot sent photo')
        return 

    def message_loop(self,botfunc, run_forever=False):
        print('TESTMODE: Bot running loop')
        cmd=''
        msg={}
        msg['chat']={}
        msg['chat']['id']=0
        for arg in sys.argv[1:]:
            if arg.find('--test')<0:cmd+=' '+arg
        msg['text']=cmd.strip()
        botfunc(msg)
        return


class qubic_bot :
    '''
    a class to send QUBIC housekeeping information via Telegram
    '''

    def __init__(self,test=False,idfile=None):
        self.TESTMODE=test
        self.botId=None
        self.bot=None
        self.timestamp_factor = 1e-3 # on and before 20181217
        self.timestamp_factor = 1

        # this list could be generated with inspect...
        self.commands = {'/start': self.start,
                         '/help': self.ayuda,
                         '/temp': self.temp_read_hk,
                         '/tempall': self.tempall,
                         '/heaters': self.read_heaters,
                         '/pressure': self.read_pressure,
                         '/mech': self.read_mech,
                         '/photo': self.photo,
                         '/photo2': self.photo2,
                         '/plot' : self.plot,
                         '/list' : self.list_channels,
                         '/entropy': self.entropy_temp,
                         '/entropy_plotall': self.entropy_plotall,
                         '/plot300mkzoom': self.entropy_plot300mKzoom,
                         '/plot300mk': self.entropy_plot300mK,
                         '/plot1k': self.entropy_plot1K
                         }

        self.known_users={504421997: 'Michel',    
                          600802212: 'Jean-Christophe',
                          610304074: 'Steve',
                          789306705: 'Jean-Pierre',
                          0: 'Test Bot'}

        self.temperature_headings = ['40K filters',
                                     '40K sd',
                                     '40K sr',
                                     'PT2 s1',
                                     'PT1 s1',
                                     '4K filters',
                                     'HWP1',
                                     'HWP2',
                                     '4K sd',
                                     '4K PT2 CH',
                                     'PT1 s2',
                                     'PT2 s2',
                                     '300mK-4CP-D-1',
                                     '300mK-4HS-D-1',
                                     '300mK-3CP-D-1',
                                     '300mK-3HS-D-1',
                                     '1K-4HS-D-1',
                                     '1K-4CP-D-1']

        self._assign_entropy_labels()

        self.temperature_display_order = [4, 3, 10, 11, 9, 6, 7, 0, 1, 2, 5, 8, 12, 13, 14, 15, 16, 17]
        temperature_heading_len = [ len(val) for val in self.temperature_headings ]
        self.temperature_heading_maxlen = max(temperature_heading_len)
        self.nTemperatures = len(self.temperature_headings)

        if 'HOME' in os.environ:
            homedir = os.environ['HOME']
        else:
            homedir = '/home/pi'
        self.hk_dir = homedir+'/data/temperature/broadcast'

        # this is not used since we implemented HK socket broadcasting 20181212
        self.temperature_log_dir = homedir+'/data/temperature/data/log_cryo/dirfile_cryo_current'

        self.time_fmt='%Y-%m-%d %H:%M:%S UT'
        
        self._init_args()
        
        if self._get_bot_id(idfile):
            self._init_bot()
            self._begin_bot()
            
        return None

    def _get_bot_id(self,filename=None):
        '''
        get the bot Id information, which is not kept on the GitHub server
        '''
        botId_file=filename
        if botId_file is None:botId_file='botId.txt'
        if not os.path.isfile(botId_file):
            print('ERROR! Could not find telebot Id: %s' % botId_file)
            return False

        h = open(botId_file,'r')
        line = h.readline()
        h.close()
        self.botId = line.strip()
        return True

    def _init_bot(self):
        '''
        initialize the Telegram bot.  Use the dummy bot if we're just testing
        '''
        if self.TESTMODE:
            print('running in test mode')
            self.bot=dummy_bot()
            self.chat_id=0            
        else:
            import telepot
            self.bot = telepot.Bot(self.botId)
            self.bot.getMe()
            
        return

    def _begin_bot(self):
        '''
        start the listening loop
        '''
        self.bot.message_loop(self._respuesta, run_forever=True)
        
        return

    def _init_args(self):
        '''
        setup the default arguments
        '''
        self.args={}
        self.args['TMIN']=None
        self.args['TMAX']=None
        self.args['DMIN']=None
        self.args['DMAX']=None
        self.args['LOGPLOT']=False
        for controller in [1,2]:
            avs = 'AVS47_%i' % controller
            self.args[avs] = range(8)
        self.args['TEMPERATURE'] = range(1, self.nTemperatures+1)
        
        return

    def _send_message(self,msg):
        '''
        send a message from the bot
        '''
        if self.bot is None:
            print('ERROR! No bot configured.')
            return
        
        self.bot.sendMessage(self.chat_id,msg)
        return

    def _send_photo(self,image):
        '''
        send an image from the bot
        '''
        self.bot.sendPhoto(self.chat_id,image)
        return

    def start(self):
        '''
        a nice message to send to first time users
        '''
        msg="Hi, I'm the Telegram bot of the QUBIC experiment.  This is the list of the available commands:"
        self._send_message(msg)
        self.ayuda()
        return

    def ayuda(self):
        '''
        some help:  This is a list of commands
        '''
        self._send_message('\n'.join(self.commands.keys()))
        return

    def temp_read_hk(self):
        '''
        read temperatures from the Housekeeping broadcast
        '''
        latest_date = dt.datetime.fromtimestamp(0)
        fmt_str = '\n%%%is:  %%7.3fK' % self.temperature_heading_maxlen
        answer = 'Temperatures:'
        for ch_idx in self.temperature_display_order:
            basename = 'TEMPERATURE%02i.txt' % (ch_idx+1)
            fullname = '%s/%s' % (self.hk_dir,basename)
            if not os.path.isfile(fullname):
                answer += '\n%s:\tno data' % self.temperature_headings[ch_idx]
            
            else:
                h = open(fullname,'r')
                lines = h.read().split('\n')
                h.close()
                lastline = lines[-2]
                cols = lastline.split()
                tstamp = self.timestamp_factor*float(cols[0])
                reading_date = dt.datetime.fromtimestamp(tstamp)
                if reading_date > latest_date:
                    latest_date = reading_date
                reading = eval(cols[1])
                answer += fmt_str % (self.temperature_headings[ch_idx],reading)

        answer += '\n\nTime: %s' % latest_date.strftime(self.time_fmt)    
        self._send_message(answer)
        return

    def temp_hk_data(self,ch=1):
        '''
        return the date,temperature data from the Housekeeping broadcast
        '''
        basename = 'TEMPERATURE%02i.txt' % ch
        fullname = '%s/%s' % (self.hk_dir,basename)
        if not os.path.isfile(fullname):
            return None,None

        h = open(fullname,'r')
        lines = h.read().split('\n')
        h.close()
        del(lines[-1])
        t=[]
        v=[]
        for line in lines:
            cols = line.split()
            tstamp = self.timestamp_factor*float(cols[0])
            reading_date = dt.datetime.fromtimestamp(tstamp)
            reading = eval(cols[1])
            t.append(reading_date)
            v.append(reading)
        return t,v
    

    def read_heaters(self):
        '''
        read the status of the heaters (power supplies)
        '''
        latest_date = dt.datetime.fromtimestamp(0)
        fmt_str = '\n%7s:  %7.3f %s %s'
        units = ['V','mA']
        answer = 'Heaters:'
        for idx in range(8):
            basename = 'HEATER%i' % (idx+1)
            for meastype_idx,meastype in enumerate(['Volt','Amp']):
                fullname = '%s/%s_%s.txt' % (self.hk_dir,basename,meastype)
                if not os.path.isfile(fullname):
                    continue
        
                h = open(fullname,'r')
                lines = h.read().split('\n')
                h.close()
                lastline = lines[-2]
                cols = lastline.split()
                tstamp = self.timestamp_factor*float(cols[0])
                reading_date = dt.datetime.fromtimestamp(tstamp)
                if reading_date > latest_date:
                    latest_date = reading_date
                reading = eval(cols[1])
                if len(cols)==3: status = cols[2]
                else: status = ''
                answer += fmt_str % (basename,reading,units[meastype_idx],status)
            answer += '\n'

        answer += 'Time: %s' % latest_date.strftime(self.time_fmt)    
        self._send_message(answer)
        return

    def read_mech(self):
        '''
        read the mechanical heat switch positions
        '''
        latest_date = dt.datetime.fromtimestamp(0)
        fmt_str = '\n%7s:  %8i'
        answer = 'Mechanical Heat Switch Positions:\n'
        for idx in range(2):
            basename = 'MHS%i' % (idx+1)
            fullname = '%s/%s.txt' % (self.hk_dir,basename)
            if not os.path.isfile(fullname):
                continue
        
            h = open(fullname,'r')
            lines = h.read().split('\n')
            h.close()
            lastline = lines[-2]
            cols = lastline.split()
            tstamp = self.timestamp_factor*float(cols[0])
            reading_date = dt.datetime.fromtimestamp(tstamp)
            if reading_date > latest_date:
                latest_date = reading_date
            reading = eval(cols[1])
            answer += fmt_str % (basename,reading)

        answer += '\n\nTime: %s' % latest_date.strftime(self.time_fmt)    
        self._send_message(answer)
        return
    
    def read_pressure(self):
        '''
        read the pressure
        '''
        latest_date = dt.datetime.fromtimestamp(0)
        fmt_str = '\n%10s:  %10.3e mbar'
        answer = 'Pressure:\n'

        idx = 0
        basename = 'PRESSURE%i' % (idx+1)
        fullname = '%s/%s.txt' % (self.hk_dir,basename)
        if not os.path.isfile(fullname):
            answer = 'No pressure.'
            answer += '\n\nTime: %s' % latest_date.strftime(self.time_fmt)    
            self._send_message(answer)
            return
        
        h = open(fullname,'r')
        lines = h.read().split('\n')
        h.close()
        lastline = lines[-2]
        cols = lastline.split()
        tstamp = self.timestamp_factor*float(cols[0])
        reading_date = dt.datetime.fromtimestamp(tstamp)
        if reading_date > latest_date:
            latest_date = reading_date
        reading = eval(cols[1])
        answer += fmt_str % (basename,reading)

        answer += '\n\nTime: %s' % latest_date.strftime(self.time_fmt)    
        self._send_message(answer)
        return
    
    def photo(self):
        '''
        take a picture of the APC QUBIC Integration Lab
        '''
        #use the web cam Pi1
        cmd='ssh pi1 ./snapshot.sh'
        subprocess.call(cmd.split())
        cmd='scp -p pi1:webcamshot.jpg .'
        subprocess.call(cmd.split())
        with open('webcamshot.jpg','r') as photo:
            self._send_photo(photo)
        return

    def photo2(self):
        '''
        take a picture of the APC QUBIC Integration Lab
        '''
        #use the web cam Pitemps
        cmd='ssh pitemps ./snapshot.sh'
        subprocess.call(cmd.split())
        cmd='scp -p pitemps:webcamshot.jpg .'
        subprocess.call(cmd.split())
        with open('webcamshot.jpg','r') as photo:
            self._send_photo(photo)
        return
    
    def entropy_latest_temperature_dir(self):
        '''
        find the location of the most recent temperature data
        '''
        entropy_dir='/entropy/logs'
    
        if not os.path.exists(entropy_dir):
            answer='Cannot read the temperatures on Entropy'
            self._send_message(answer)
            return None

        dlist=[]
        for r,d,f in os.walk(entropy_dir):
            if r!=entropy_dir:
                dlist.append(r)

        dlist.sort(key=os.path.getmtime)
        tempdir=dlist[-1]
        return tempdir


    def _assign_entropy_labels(self):
        '''                                                                                                      
        read temperature labels from the Entropy Windows machine, shared by Samba
        '''
        tempdir=self.entropy_latest_temperature_dir()
        if tempdir is None:return None

        # default labels
        self.entropy_channel_title={}
        self.entropy_channel_title['AVS47_1']=[]
        self.entropy_channel_title['AVS47_2']=[]
        for ch in range(8):
            for avs in ['AVS47_1','AVS47_2']:
                default_label='%s ch%i' % (avs,ch)
                self.entropy_channel_title[avs].append(default_label)

        # read the configured labels
        filelist=glob(tempdir+'/*')
        for f in filelist:
            chan_str = re.sub('\.log','',os.path.basename(f))
            match_str = '.* AVS47 (AVS47_[12]) Ch ([0-7]) '
            match = re.match(match_str,chan_str)
            chan_str = re.sub(match_str,'',chan_str)
            if match:
                avs=match.group(1)
                ch=eval(match.group(2))
                self.entropy_channel_title[avs][ch]=chan_str

        return
    
    def entropy_temp(self):
        '''                                                                                                      
        read temperatures from the Entropy Windows machine, shared by Samba
        '''
        tempdir=self.entropy_latest_temperature_dir()
        if tempdir is None:return tempdir

        latest_date = dt.datetime.fromtimestamp(0)
    
        answer=''
        filelist=glob(tempdir+'/*')
        for f in filelist:
            chan_str=re.sub('\.log','',os.path.basename(f))
            chan_str=re.sub('.* AVS47 AVS47_[12] Ch [0-7] ','',chan_str)
            h=open(f,'r')
            lines=h.read().split('\n')
            h.close()
            del(h)

            for line in lines:
                if line.find('#Log session timestamp:')==0:
                    # get start time from header
                    tstart_str=line.replace('#Log session timestamp:','')
                    try:
                        tstart=eval(tstart_str)*1e-3 - 3600
                    except:
                        tstart=-1
                    break
        
            lastline=lines[-2]
            cols=lastline.split()
            val=float(cols[1])
            if len(cols)==3:
                if val<1:
                    fmt_str = '\n%s : %.1f mK'
                    val *= 1000
                else:
                    fmt_str = '\n%s : %.3f K'
                tempans=fmt_str % (chan_str,val)
            else:
                tempans='\n%s : %.4f Ohm' % (chan_str,val)        
            if tempans.find('MCST3601')<0:
                answer+=tempans

            tstamp = 1e-3*eval(cols[0]) + tstart
            reading_date = dt.datetime.fromtimestamp(tstamp)
            if reading_date > latest_date:
                latest_date = reading_date
            
        now='\n\nTime: %s' % latest_date.strftime(self.time_fmt)
        answer+=now
    
        self._send_message(answer)
        return answer
        
    def read_entropy_logfile(self,filename):
        '''
        read a temperature log file produced by Entropy
        '''
        if not os.path.exists(filename):
            print('file not found: %s' % filename)
            return None,None
        if not os.path.isfile(filename):
            print('this is not a file: %s' % filename)
            return None,None

        h=open(filename,'r')
        lines=h.read().split('\n')
        h.close()

        # go through the lines
        t=[]
        val=[]
        for line in lines:
            if line.find('#')!=0:
                cols=line.split()
                try:
                    tt=eval(cols[0])*1e-3
                    yy=eval(cols[1])
                    t.append(tt)
                    val.append(yy)
                
                except:
                    #print('DEBUG: unable to interpret: %s' % line)
                    pass
            elif line.find('#Log session timestamp:')==0:
                # get start time from header
                tstart_str=line.replace('#Log session timestamp:','')
                try:
                    tstart=eval(tstart_str)*1e-3
                except:
                    tstart=-1

        #print('DEBUG: tstart = %f' % tstart)
        t=np.array(t)
        #print(t)
        val=np.array(val)
        #print(val)
        tdate=[]
        if tstart>0:
            t+=tstart
            for tstamp in t:
                tdate.append(dt.datetime.fromtimestamp(tstamp))
        else:
            tdate=t

        return tdate,val

    def tempall(self):
        '''
        print out all the temperatures
        '''
        self.entropy_temp()
        self.temp_read_hk()
        return

    
    def plot_temperature(self,t,v,title,dmin=None,dmax=None,Tmin=None,Tmax=None,logscale=False):
        '''
        make a quick plot of the temperature cooldown/warmup
        '''

        plt.ioff()
        fig=plt.figure(figsize=(20.48,7.68))
        plt.plot(t,v)
        ax=fig.axes[0]
        if Tmin is None:Tmin=min(v)
        if Tmax is None:Tmax=max(v)
        if dmin is None:dmin=t[0]
        if dmax is None:dmax=t[-1]
        ax.set_ylim(Tmin,Tmax)
        ax.set_xlim(dmin,dmax)
        
        
        ax.set_xlabel('date')
        ax.set_ylabel('temperature / K')
        fig.suptitle(title)
        savefig_fmt='png'
        fig.savefig('temperature_plot.'+savefig_fmt,format=savefig_fmt,dpi=100,bbox_inches='tight')
    
        plt.close()
        return

    def entropy_plot_channel(self,controller=1,channel=1,dmin=None,dmax=None,Tmin=None,Tmax=None,logscale=False):
        '''
        plot a given channel
        '''
        tempdir=self.entropy_latest_temperature_dir()
        if tempdir is None:return tempdir

        filename=''
        find_str='.* AVS47_%i Ch (%i)' % (controller,channel)

        filelist=glob(tempdir+'/*')
        for f in filelist:
            match=re.match(find_str,f)
            if match:
                filename=f
                break

        print('DEBUG: filename=%s' % filename)
        t,v=read_entropy_logfile(filename)
        if t is None:
            answer='No MACRT temperatures on Entropy'
            self._send_message(answer)
            return answer

        result=self.plot_temperature(t,v,entropy_channel_title[channel],
                                     dmin=dmin,dmax=dmax,Tmin=Tmin,Tmax=Tmax,logscale=logscale)
        with open('temperature_plot.png','r') as plot:
            bot.sendPhoto(chat_id,plot)
        return

    def entropy_channel_data(self,controller=1,channel=1):
        '''
        get the date,temperature data from one of the Entropy temperature sensors
        '''
        tempdir=self.entropy_latest_temperature_dir()
        if tempdir is None:return None,None

        filename=''
        find_str='.* AVS47_%i Ch (%i)' % (controller,channel)

        filelist=glob(tempdir+'/*')
        for f in filelist:
            match=re.match(find_str,f)
            if match:
                filename=f
                break

        t,v = self.read_entropy_logfile(filename)
        return t,v
        


    def entropy_plot1K(self):
        '''
        make a plot of the 1K stage and send it via telegram
        '''
        return self.entropy_plot_channel(channel=1)

    def entropy_plot300mK(self):
        '''
        plot the 0.3K stage and send it via telegram
        '''
        return self.entropy_plot_channel(channel=2)

    def entropy_plot300mKzoom(self):
        '''
        plot the last hour of 300mK data
        '''
        tempdir=self.entropy_latest_temperature_dir()
        if tempdir is None:return tempdir
        channel=2
        filename=''
        find_str='.* Ch (%i)' % channel
        filelist=glob(tempdir+'/*')
        for f in filelist:
            match=re.match(find_str,f)
            if match:
                filename=f
                break

        t,v=read_entropy_logfile(filename)
        if t is None:
            answer='No MACRT temperatures on Entropy'
            self._send_message(answer)
            return answer

        dmax=t[-1]
        dmin=dmax-dt.timedelta(minutes=60)
        for idx,dd in enumerate(t):
            if dd>dmin:
                imin=idx
                break
        Tmin=min(v[imin:])
        Tmax=max(v[imin:])
    
        result=self.plot_temperature(t,v,entropy_channel_title[channel],dmin,dmax,Tmin,Tmax)
        with open('temperature_plot.png','r') as plot:
            self._send_photo(plot)
        return

    def entropy_plotall(self,Tmin=None,Tmax=None):
        '''
        plot all temperatures available from entropy
        '''
        tempdir=self.entropy_latest_temperature_dir()
        if tempdir is None:return tempdir

        plt.ioff()
        fig=plt.figure(figsize=(20.48,7.68))

        filelist=glob(tempdir+'/*')
        Tminlist=[]
        Tmaxlist=[]
        for f in filelist:
            print(f)
            find_str='.* Ch ([0-%i])' % (entropy_nchannels-1)
            match=re.match(find_str,f)
            if match:
                idx=eval(match.group(1))
                t,v=read_entropy_logfile(f)
                Tminlist.append(min(v))
                Tmaxlist.append(max(v))
                if t is not None:plt.plot(t,v,label=entropy_channel_title[idx])
        if Tmin is None:
            Tmin = min(Tminlist)
        if Tmax is None:
            Tmax = max(Tmaxlist)
        ax=fig.axes[0]
        ax.set_ylim((Tmin,Tmax))
        ax.set_xlabel('date')
        ax.set_ylabel('temperature / K')
        fig.suptitle('Temperatures from the AVS47')
        plt.legend()
        fig.savefig('temperature_plot.png',format='png',dpi=100,bbox_inches='tight')
        plt.close()
        with open('temperature_plot.png','r') as plot:
            self._send_photo(plot)
        return

    def plot(self):
        '''
        this is a generic plot using the parsed arguments
        '''
        if self.args is not None:
            print('I found the following keys:')
            for key in self.args.keys():
                print('%s: %s' % (key,self.args[key]))
        else:
            print("I didn't find any arguments")


        
        plt.ioff()
        fig=plt.figure(figsize=(20.48,7.68))
        tmin_list=[]
        tmax_list=[]
        dmin_list=[]
        dmax_list=[]
        
        # plot temperature diodes
        for ch in self.args['TEMPERATURE']:
            ch_idx = ch-1
            t,v=self.temp_hk_data(ch)
            if (t is not None) and (v is not None):
                channel_label=self.temperature_headings[ch_idx]
                plt.plot(t,v,label=channel_label)
                tmax_list.append(max(v))
                tmin_list.append(min(v))
                dmax_list.append(max(t))
                dmin_list.append(min(t))

        # plot AVS47 temperatures
        for controller in [1,2]:
            avs = 'AVS47_%i' % controller
            for ch in self.args[avs]:
                t,v = self.entropy_channel_data(controller,ch)
                if (t is not None) and (v is not None):
                    entropy_label=self.entropy_channel_title[avs][ch]
                    plt.plot(t,v,label=entropy_label)                
                    tmax_list.append(max(v))
                    tmin_list.append(min(v))
                    dmax_list.append(max(t))
                    dmin_list.append(min(t))
                
        Tmin=min(tmin_list)
        Tmax=max(tmax_list)
        if self.args['TMIN'] is not None:
            Tmin=self.args['TMIN']
        if self.args['TMAX'] is not None:
            Tmax=self.args['TMAX']
            
        dmin=min(dmin_list)
        dmax=max(dmax_list)
        if self.args['DMIN'] is not None:
            dmin=self.args['DMIN']
        if self.args['DMAX'] is not None:
            dmax=self.args['DMAX']
            
        ax=fig.axes[0]
        ax.set_xlim((dmin,dmax))
        ax.set_ylim((Tmin,Tmax))
        ax.set_xlabel('date')
        ax.set_ylabel('temperature / K')
        fig.suptitle('Temperatures')
        plt.legend()
        fig.savefig('temperature_plot.png',format='png',dpi=100,bbox_inches='tight')
        plt.close()
        with open('temperature_plot.png','r') as plot:
            self._send_photo(plot)
        return

    def list_channels(self):
        '''
        return a list of all the temperature channels
        '''
        answer = ''
        # entropy
        for avs in ['AVS47_1','AVS47_2']:
            for ch in range(8):
                txt='%s_ch%i = %s\n' % (avs,ch,self.entropy_channel_title[avs][ch])
                answer += txt
            answer += '\n'

        for idx,label in enumerate(self.temperature_headings):
            txt = 'TEMPERATURE%02i = %s\n' % (idx+1,label)
            answer += txt

        self._send_message(answer)
        return
    
    def _default_answer(self):
        '''
        the default reply to unknown commands
        '''
        ans="I don't understand that command yet."
        if self.chat_id in self.known_users.keys():
            ans='Sorry %s, %s' % (self.known_users[self.chat_id],ans)
        self._send_message(ans)
        return

    def _parseargs(self,args_list):
        '''
        parse the arguments that were sent to the bot
        '''
        self._init_args()
        for arg in args_list:
            keyarg = arg.split('=')
            if len(keyarg)==2:
                key = keyarg[0].upper()
                if key=='AVS1':key='AVS47_1'
                if key=='AVS2':key='AVS47_2'
                if key=='T' or key=='TEMP':key='TEMPERATURE'
                if key=='DMIN' or key=='DMAX':
                    print('DEBUG: trying to convert date: %s' % keyarg[1])
                    print('DEBUG: this argument is of type: %s' % type(keyarg[1]))
                    _arg = str2dt( str(keyarg[1]) )
                else:
                    try:
                        _arg = eval(keyarg[1])
                    except:
                        _arg = keyarg[1]
            else:
                key=arg
                _arg=True
            self.args[key]=_arg

        for key in ['AVS47_1','AVS47_2','TEMPERATURE']:
            if self.args[key]=='':continue
            if not isinstance(self.args[key],list) and not isinstance(self.args[key],tuple):
                self.args[key]=[self.args[key]]
            
        return

    def _respuesta(self,msg):
        '''
        this is the message receiver
        '''
        self.chat_id = msg['chat']['id']
        cmd = msg['text']
        cmd_list = cmd.split()
        if len(cmd_list)>1:
            self._parseargs(cmd_list[1:])

        now=dt.datetime.utcnow()
        user='unknown'
        if self.chat_id in self.known_users.keys():user=self.known_users[self.chat_id]
        msg="%s %i %16s %s" % (now.strftime(self.time_fmt),self.chat_id, user, cmd)
    
        print(msg)
        h=open('bot.log','a')
        h.write(msg+'\n')
        h.close()

        if len(cmd_list)>0:
            run_cmd = cmd_list[0].lower()
            if run_cmd.find('/')!=0:run_cmd='/'+run_cmd
            if run_cmd in self.commands.keys():
                self.commands[run_cmd]()
            else:
                self._default_answer()
        else:
            self.commands['/start']()
        return



