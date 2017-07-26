#!/usr/bin/env python
"""
$Id: iv.py

$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
$created: Wed 05 Jul 2017 14:39:42 CEST
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

get data from QubicStudio and plot hysterisis I-V curves 
refresh and replot

"""
from __future__ import division, print_function
import numpy as np
import pystudio
import sys,os,time
import datetime as dt
import matplotlib.pyplot as plt
from glob import glob
import math

def wait_a_bit(self,pausetime=None):
    if pausetime==None:
        pausetime=self.pausetime
    else:
        self.assign_pausetime(pausetime)
        
    print("waiting %.3f seconds" % pausetime)
    time.sleep(pausetime)
    return

def ADU2I(self,ADU, offset=None, fudge=1.0):
    ''' 
    This is the magic formula to convert the measured output of the TES to current
    the voltage (ADU) returned by the TES is converted to a current in uA        
    '''
    Rfb   = 10000. # Ohm
    q_ADC = 20./(2**16-1)
    G_FLL = (10.4 / 0.2) * Rfb
    I = 1e6 * (ADU / 2**7) * (q_ADC/G_FLL) * (self.nsamples - 8) * fudge

    if offset!=None: return I+offset
    return I

def find_normalization(self,I,Vbias):
    '''
    The normalization forces the equivalent circuit to have a resistance of 1 Ohm
    We do this at the maximum Vbias.
    Ohm's law: V=IR
    '''
    R=Vbias/(I/1.0e6) # I in uA
    K=1./R
    return abs(K)

def find_offset(self,I,Vbias):
    '''
    the offset is chosen to have the equivalent of R=1 Ohm
    We do this at the maximum Voffset

    I_prime=Imeas-I_maxbias+Vmaxbias/R

    '''
    R=1.0
    Ioffset=-I+Vbias/R
    return Ioffset
    

def setup_plot_Vavg(self,axes=None):
    ttl=str('Average Current per TES with different Vbias')
    plt.ion()
    fig=plt.figure(figsize=self.figsize)
    fig.canvas.set_window_title('plt: '+ttl) 
    fig.suptitle(ttl,fontsize=16)
    if axes != None: plt.axis(axes)
    plt.xlabel('TES number')
    plt.ylabel('I  /  $\mu$A')
    return fig

def plot_Vavg(self,Vavg,Vbias,offset=None,axes=None):
    Iavg=self.ADU2I(Vavg,offset)
    
    lbl=str('V$_{bias}$ = %.2fV' % Vbias)
    plt.cla()
    if axes != None: plt.axis(axes)
    plt.xlabel('TES number')
    plt.ylabel('I  /  $\mu$A')
    # plot markers with no lines
    plt.plot(Iavg,marker='D',drawstyle='steps-mid',linestyle='none',color='green',label=lbl)
    # plot bars up to the markers
    tes_axis=np.arange(self.NPIXELS)-0.25
    plt.bar(tes_axis,height=Iavg,color='pink',width=0.5)
    plt.legend()
    plt.pause(0.01)
    return

def plot_iv_all(self,selection=None):
    if self.vbias==None:
        self.vbias=make_Vbias()
    if isinstance(self.obsdate,dt.datetime):
        ttl=str('QUBIC I-V curves (%s)' % (self.obsdate.strftime('%Y-%b-%d %H:%M UTC')))
    else:
        ttl=str('QUBIC I-V curve per TES with Vbias ranging from %.2fV to %.2fV' % (self.min_bias,self.max_bias))
    if selection != None:
        nselection=0
        for val in selection:
            if val: nselection+=1
    else:
        nselection=self.NPIXELS
                
    subttl=str('plotting curves for %i TES out of %i' % (nselection,self.NPIXELS))
    plt.ion()
    fig=plt.figure(figsize=self.figsize)
    fig.canvas.set_window_title('plt: '+ttl) 
    fig.suptitle(ttl+'\n'+subttl,fontsize=16)
    plt.xlabel('Bias Voltage  /  V')
    plt.ylabel('Current  /  $\mu$A')

    nbias=self.v_tes.shape[1]
    Ntes=self.v_tes.shape[0]
    
    offset=[]
    colour_idx=0
    ncolours=len(self.colours)
    for n in range(Ntes):

        if (selection==None) or (selection[n]):
            I=self.ADU2I(self.v_tes[n,self.max_bias_position])
            # offset the Current so that R=1 Ohm at the highest Vbias
            offset=self.find_offset(I,self.max_bias)
            
            Iavg=self.ADU2I(self.v_tes[n,:],offset)

            if colour_idx >= ncolours:colour_idx=0
            self.draw_iv(Iavg,colour=self.colours[colour_idx])
            colour_idx+=1

    pngname=str('TES_IV_ASIC%i_all_%s.png' % (self.asic,self.obsdate.strftime('%Y%m%dT%H%M%SUTC')))
    plt.savefig(pngname,format='png',dpi=100,bbox_inches='tight')
    plt.show()
    return fig

def setup_plot_iv_multi(self,nrows=16,ncols=8):
    if self.vbias==None: self.vbias=make_Vbias()
    if isinstance(self.obsdate,dt.datetime):
        ttl=str('QUBIC I-V curves (%s)' % (self.obsdate.strftime('%Y-%b-%d %H:%M UTC')))
    else:
        ttl=str('QUBIC I-V curve per TES with Vbias ranging from %.2fV to %.2fV' % (self.min_bias,self.max_bias))

    nbad=0
    if not self.filterinfo==None:
        for val in self.filterinfo['is_good']:
            if not val:nbad+=1
        ttl+=str('\n%i flagged as bad pixels' % nbad)
    
    plt.ion()
    fig,axes=plt.subplots(nrows,ncols,sharex=True,sharey=False,figsize=self.figsize)
    fig.canvas.set_window_title('plt: '+ttl)
    fig.suptitle(ttl,fontsize=16)
    plt.xlabel('Bias Voltage  /  V')
    plt.ylabel('Current  /  $\mu$A')
    return fig,axes

def plot_iv_multi(self):
    '''
    plot all TES I-V curves on a grid
    the optional list "is_good" is boolean for each TES
    if present, a label will be shown on each curve indicating 
    whether that TES is considered good or not
    '''
    if not self.filterinfo==None: ngood=self.filterinfo['ngood']
    nrows=16
    ncols=8
    fig,axes=self.setup_plot_iv_multi(nrows,ncols)
    
    tes_index=0
    for row in range(nrows):
        for col in range(ncols):
            axes[row,col].get_xaxis().set_visible(False)
            axes[row,col].get_yaxis().set_visible(False)

            I=self.ADU2I(self.v_tes[tes_index,self.max_bias_position])
            # offset the Current so that R=1 Ohm at the highest Vbias
            offset=self.find_offset(I,self.max_bias)
            Iavg=self.ADU2I(self.v_tes[tes_index,:],offset)            
            self.draw_iv(Iavg,colour='blue',axis=axes[row,col])
            text_y=min(Iavg)
            axes[row,col].text(self.max_bias,text_y,str('%i' % (tes_index+1)),va='bottom',ha='right',color='black')

            if (not self.filterinfo==None)\
               and (not self.filterinfo['is_good']==None)\
               and (not self.filterinfo['is_good'][tes_index]):
                # axes[row,col].text(self.min_bias,text_y,'BAD',va='bottom',ha='left',color='red')
                axes[row,col].set_axis_bgcolor('red')

            tes_index+=1

    pngname=str('TES_IV_ASIC%i_thumbnail_%s.png' % (self.asic,self.obsdate.strftime('%Y%m%dT%H%M%SUTC')))
    plt.savefig(pngname,format='png',dpi=100,bbox_inches='tight')
    plt.show()
    
    return fig

def plot_iv_physical_layout(self):
    '''
    plot the I-V curves in thumbnails mapped to the physical location of each detector
    '''
    ttl=str('QUBIC I-V curves (%s)' % (self.obsdate.strftime('%Y-%b-%d %H:%M UTC')))

    if not self.filterinfo==None:
        ngood=self.filterinfo['ngood']
    else:
        ngood=None
    
    nrows=self.pix_grid.shape[0]
    ncols=self.pix_grid.shape[1]

    plt.ion()
    fig,ax=plt.subplots(nrows,ncols,figsize=self.figsize)
    subttl=str('ASIC #%i' % self.asic)
    if not ngood==None:
        subttl+=str(': %i flagged as bad pixels' % (self.NPIXELS-ngood))
    pngname=str('TES_IV_ASIC%i_%s.png' % (self.asic,self.obsdate.strftime('%Y%m%dT%H%M%SUTC')))
    fig.canvas.set_window_title('plt:  '+ttl)
    fig.suptitle(ttl+'\n'+subttl,fontsize=16)
    

    # the pixel number is between 1 and 248
    TES_translation_table=self.tes2pix[self.asic_index()]

    for row in range(nrows):
        for col in range(ncols):
            TES=0
            ax[row,col].get_xaxis().set_visible(False)
            ax[row,col].get_yaxis().set_visible(False)
            ax[row,col].set_xlim([self.min_bias,self.max_bias])
            # ax[row,col].set_ylim([self.min_bias,self.max_bias])
            # ax[row,col].set(aspect=1)

            # the pixel identity associated with its physical location in the array
            physpix=self.pix_grid[row,col]
            pix_index=physpix-1
            
            text_y=0.0
            if physpix==0:
                pix_label='EMPTY'
                label_colour='white'
                face_colour='black'
            elif physpix in TES_translation_table:
                TES=self.pix2tes[self.asic_index(),pix_index]
                pix_label=str('%i' % TES)
                label_colour='black'
                face_colour='white'
                TES_index=self.TES_index(TES)
                I=self.ADU2I(self.v_tes[TES_index,self.max_bias_position])
                # offset the Current so that R=1 Ohm at the highest Vbias
                offset=self.find_offset(I,self.max_bias)
                Iavg=self.ADU2I(self.v_tes[TES_index,:],offset)            
                text_y=min(Iavg)
                self.draw_iv(Iavg,colour='blue',axis=ax[row,col])

                if (not self.filterinfo['is_good']==None) and (not self.filterinfo['is_good'][TES_index]):
                    face_colour='red'
                    label_colour='white'
                    # ax[row,col].text(self.min_bias,text_y,'BAD',va='bottom',ha='left',color=label_colour)
            else:
                pix_label='other\nASIC'
                label_colour='yellow'
                face_colour='blue'
                
            ax[row,col].set_axis_bgcolor(face_colour)
            ax[row,col].text(self.max_bias,text_y,pix_label,va='bottom',ha='right',color=label_colour,fontsize=8)
            
    plt.savefig(pngname,format='png',dpi=100,bbox_inches='tight')
    plt.show()

    return


def make_line(self,pt1,pt2,xmin,xmax):
    '''
    make a line with extents xmin,xmax which includes the two points pt1, and pt2
    y=mx+b
    '''
    m = (pt2[1]-pt1[1]) / (pt2[0]-pt1[0])
    b = pt1[1] - (m*pt1[0])

    ymin=m*xmin+b
    ymax=m*xmax+b
    print('straight line should go through the origin: b=%.5e =  0?' % b)
    return [ymin,ymax]


def fit_iv(self,I):
    '''
    fit the I-V curve to a polynomial
    '''

    # return is a dictionary with various info
    ret={}

    if self.cycle_vbias:
        # only fit half the points
        # fit the second half which is often better
        mid=int(len(self.vbias)/2)
        ypts=I[mid:len(self.vbias)]
        xpts=self.vbias[mid:len(self.vbias)]
        npts=len(xpts)
    else:
        ypts=I
        xpts=self.vbias
        npts=len(I)

    # fit to polynomial degree 3
    fitinfo=np.polyfit(xpts,ypts,3,full=True)
    ret['fitinfo']=fitinfo

    # find inflection where polynomial tangent is zero (i.e. first derivative is zero)
    a3=fitinfo[0][0]
    a2=fitinfo[0][1]
    a1=fitinfo[0][2]
    a0=fitinfo[0][3]

    t1=-a2/(3*a3)
    discriminant=a2**2 - 3*a1*a3
    if discriminant<0.0:
        ret['inflection']=[None,None]
        ret['concavity']=[None,None]
        return ret

    t2=math.sqrt(discriminant)/(3*a3)
    x0_0=t1+t2
    x0_1=t1-t2
    ret['inflection']=[x0_0,x0_1]

    # check the concavity of the inflection: up or down (+ve is up)
    ret['concavity']=[2*a2 + 6*a3*x0_0, 2*a2 + 6*a3*x0_1]
    
    return ret


def draw_iv(self,I,colour='blue',axis=plt):
    '''
    draw an individual I-V curve
    '''

    npts=len(I)
    if npts<len(self.vbias) and npts>0:
        # this is a partial curve
        plt.cla()
        axis.set_xlim([self.min_bias,self.max_bias])
        # axis.set_ylim([min(self.vbias),max(self.vbias)])

        # we mark the last point
        axis.plot(self.vbias[0:npts],I,color=colour)
        axis.plot(self.vbias[npts-1],I[npts-1],color='red',marker='D',linestyle='none')
        plt.pause(0.01)
        return
    
    if self.cycle_vbias:
        # plot down and up voltage with different linestyles
        mid=int(len(self.vbias)/2)
        axis.plot(self.vbias[0:mid],I[0:mid],linestyle='solid', color=colour)
        axis.plot(self.vbias[mid:-1], I[mid:-1], linestyle='dashed',color=colour)
        return
    
    axis.plot(self.vbias,I,color=colour)
    return

def setup_plot_iv(self,TES,xwin=True):
    if isinstance(self.obsdate,dt.datetime):
        ttl=str('QUBIC I-V curve for TES#%3i (%s)' % (TES,self.obsdate.strftime('%Y-%b-%d %H:%M UTC')))
    else:
        ttl=str('QUBIC I-V curve for TES#%3i with Vbias ranging from %.2fV to %.2fV' % (TES,self.min_bias,self.max_bias))
    subttl=str('ASIC #%i' % self.asic)
    if xwin: plt.ion()
    else: plt.ioff()
    fig,ax=plt.subplots(1,1,figsize=self.figsize)
    fig.canvas.set_window_title('plt: '+ttl) 
    fig.suptitle(ttl+'\n'+subttl,fontsize=16)
    ax.set_xlabel('Bias Voltage  /  V')
    ax.set_ylabel('Current  /  $\mu$A')
    ax.set_xlim([self.min_bias,self.max_bias])
    # ax.set_ylim([self.min_bias,self.max_bias])
    return fig,ax

def plot_iv(self,TES=None,offset=None,fudge=1.0,multi=False,xwin=True):
    if multi:return self.plot_iv_multi()
    if TES==None:return self.plot_iv_all()
    if not isinstance(TES,int): return self.plot_iv_all()

    TES_index=self.TES_index(TES)
    
    if self.vbias==None: self.vbias=make_Vbias()
    
    # normalize the Current so that R=1 Ohm at the highest Voffset
    Vbias=self.vbias[self.max_bias_position]
    I=self.ADU2I(self.v_tes[TES_index,self.max_bias_position])
    if offset==None: offset=self.find_offset(I,Vbias)
    txt=str('offset=%.4e' % offset)

    fig,ax=self.setup_plot_iv(TES,xwin)
    
    Iavg=self.ADU2I(self.v_tes[TES_index,:],offset=offset,fudge=fudge)
    self.draw_iv(Iavg)

    # draw a polynomial fit to the I-V curve
    fit=self.fit_iv(Iavg)
    txt+=str('\npolynomial fit residual: %.4e' % fit['fitinfo'][1][0])
    f=np.poly1d(fit['fitinfo'][0])
    plt.plot(self.vbias,f(self.vbias),linestyle='dashed',color='red')

    # note the turnover point
    found_turnover=False
    for n in range(2):
        v0=fit['inflection'][n]
        concavity=fit['concavity'][n]
        if (not v0==None) and v0>self.min_bias and v0<self.max_bias and concavity>0:
            xpts=[v0,v0]
            ypts=[min(Iavg),max(Iavg)]
            plt.plot(xpts,ypts,linestyle='dashed',color='green')
            found_turnover=True
            txt+=str('\nturnover Vbias=%.2fV' % v0)
    if not found_turnover:
        txt+='\nNo turnover!'
        
    
    # draw a line tangent to the final points
    I1=self.ADU2I(self.v_tes[TES_index,self.max_bias_position],offset=offset,fudge=fudge)
    bias1=self.max_bias
    pos2=self.max_bias_position-2
    if pos2<0: pos2=self.max_bias_position+2
        
    bias2=self.vbias[pos2]
    I2=self.ADU2I(self.v_tes[TES_index,pos2],offset=offset,fudge=fudge)
    pt1=[bias1,I1]
    pt2=[bias2,I2]
    I_R1=self.make_line(pt1,pt2,self.min_bias,self.max_bias)
    plt.plot([self.min_bias,self.max_bias],I_R1,linestyle='dashed',color='green')


    # if we've already run the filter, add a comment if flagged bad
    if not self.filterinfo==None:
        if not self.filterinfo['is_good'][TES_index]:
            txt+=str('\nFlagged as BAD:  %s' % self.filterinfo['comment'][TES_index])
    # write out the comments
    text_x=self.min_bias + 0.95*(self.max_bias-self.min_bias)
    text_y=min(Iavg) + 0.98*(max(Iavg)-min(Iavg))
    plt.text(text_x,text_y,txt,va='top',ha='right',fontsize=12)
    pngname=str('TES%03i_IV_ASIC%i_%s.png' % (TES,self.asic,self.obsdate.strftime('%Y%m%dT%H%M%SUTC')))
    plt.savefig(pngname,format='png',dpi=100,bbox_inches='tight')
    if xwin:
        plt.show()
    else:
        plt.clf()
        plt.close()
    return fig

def make_Vbias(self,cycle_voltage=None,vmin=5.0,vmax=8.0,dv=0.04,lowhigh=True):
    '''
    the bias voltage values used during the I-V curve measurement
    '''
    if cycle_voltage==None:cycle_voltage=self.cycle_vbias
    going_up=np.arange(vmin,vmax+dv,dv)
    going_dn=np.flip(going_up,0)

    if cycle_voltage:
        if lowhigh:
            vbias=np.concatenate((going_up,going_dn),0)
        else:
            vbias=np.concatenate((going_dn,going_up),0)
    else:
        if lowhigh:
            vbias=going_up
        else:
            vbias=going_dn
            
    self.vbias=vbias
    self.cycle_vbias=cycle_voltage
    self.min_bias=min(self.vbias)
    self.max_bias=max(self.vbias)
    self.max_bias_position=np.argmax(self.vbias)
    return vbias

def get_Vavg_data(self):
    '''
    DEPRECATED! use get_IV_data() instead
    '''
    print('DEPRECATION WARNING! Please use get_IV_data().')
    client = self.connect_QubicStudio()
    if client==None: return None

    ofilename = dt.datetime.utcnow().strftime("test_vi_%Y%m%dT%H%M%SUTC.txt")

    if self.vbias==None: vbias=make_Vbias()
    nbias=len(vbias)

    v_tes = np.empty((self.NPIXELS,nbias))

    fig,ax=self.setup_plot_Vavg()
    for j in range(nbias) :
        print("measures at Voffset=%gV " % vbias[j])
        self.set_VoffsetTES(vbias[j],0.0,self.asic_index())
        self.wait_a_bit()
        Vavg= self.get_mean(tinteg,asic)
        print ("a sample of V averages :  %g %g %g " %(Vavg[0], Vavg[43], Vavg[73]) )
        v_tes[:,j]=Vavg
        self.plot_Vavg(Vavg,vbias[j])


    plt.show()
    np.savetxt(ofilename, v_tes,delimiter="\t")
    self.assign_Vtes(v_tes)
    return v_tes

def get_IV_data(self,replay=False,TES=None,monitor=False):
    '''
    get IV data and make a running plot
    optionally, replay saved data.

    you can monitor the progress of a given TES by the keyword TES=<number>

    setting monitor=True will monitor *all* the TES, but this slows everything down
    enormously!  Not recommended!!

    '''

    monitor_iv=False
    if not TES==None:
        monitor_TES_index=self.TES_index(TES)
        monitor_iv=True

    if replay:
        if self.v_tes==None:
            print('Please read an I-V data file, or run a new measurement!')
            return None
        if self.vbias==None:
            print('There appears to be I-V data, but no Vbias info.')
            print('Please run make_Vbias() with the correct max and min values')
            return None
        vbias=self.vbias
        v_tes=self.v_tes
    else:
        client = self.connect_QubicStudio()
        if client==None: return None
        self.obsdate=dt.datetime.utcnow()
        if self.vbias==None: vbias=make_Vbias()
        v_tes = np.empty((self.NPIXELS,nbias))

        
    nbias=len(vbias)

    figavg=self.setup_plot_Vavg()
    if monitor_iv:figiv,axiv=self.setup_plot_iv(TES)
    if monitor:
        nrows=16
        ncols=8
        figmulti,axmulti=self.setup_plot_iv_multi()
    
    for j in range(nbias) :
        print("measures at Voffset=%gV " % vbias[j])
        if not replay:
            self.set_VoffsetTES(vbias[j],0.0)
            self.wait_a_bit()
            Vavg= self.get_mean()
            v_tes[:,j]=Vavg
        else:
            Vavg=v_tes[:,j]

        print ("a sample of V averages :  %g %g %g " %(Vavg[0], Vavg[43], Vavg[73]) )
        plt.figure(figavg.number)
        self.plot_Vavg(Vavg,vbias[j])
        if monitor_iv:
            plt.figure(figiv.number)
            I_tes=v_tes[monitor_TES_index,0:j+1]
            Iavg=self.ADU2I(I_tes)
            self.draw_iv(Iavg,axis=axiv)

        if monitor:
            # monitor all the I-V curves:  Warning!  Extremely slow!!!
            TES_index=0
            for row in range(nrows):
                for col in range(ncols):
                    axmulti[row,col].get_xaxis().set_visible(False)
                    axmulti[row,col].get_yaxis().set_visible(False)

                    Iavg=self.ADU2I(self.v_tes[TES_index,0:j+1])
                    self.draw_iv(Iavg,colour='blue',axis=axmulti[row,col])
                    text_y=min(Iavg)
                    axmulti[row,col].text(max(self.vbias),text_y,str('%i' % (TES_index+1)),va='bottom',ha='right',color='black')
            
                    TES_index+=1
        


    plt.show()
    self.assign_Vtes(v_tes)
    if not replay:
        self.write_fits()
    
    return v_tes

def filter_Vtes(self,residual_limit=3.0,abs_amplitude_limit=0.01,rel_amplitude_limit=0.1,bias_margin=0.2):
    '''
    find which TES are good
    '''
    if self.v_tes==None:
        print('No data!  Please read a file, or run a measurement.')
        return None

    # a dictionary for returned stuff
    ret={}
    
    I_offset=np.zeros(self.NPIXELS)
    is_good=[]
    comment=[]
    turnover=[]
    for TES_index in range(self.NPIXELS):
        is_good.append(True)
        comment.append('no comment')
        turnover.append(None)


    # go through each filter.  Jump out and examine the next I-V curve as soon as a bad I-V is found
    good_index=[]
    for TES_index in range(self.NPIXELS):
        # normalize the Current so that R=1 Ohm at the highest Voffset
        Vbias=self.vbias[self.max_bias_position]
        I=self.ADU2I(self.v_tes[TES_index,self.max_bias_position])
        offset=self.find_offset(I,Vbias)
        I_offset[TES_index]=offset
        Iavg=self.ADU2I(self.v_tes[TES_index,:],offset=offset)

        # fit to a polynomial. The fit will be for the second half if it's cycled bias
        fit=self.fit_iv(Iavg) 
        residual=fit['fitinfo'][1][0]

        # first filter:  is it a good fit?
        if residual>residual_limit:
            is_good[TES_index]=False
            comment[TES_index]='bad poly fit'
            continue
    
        # second filter: small amplitude is rejected
        # consider only the second half if it's cycled bias
        if self.cycle_vbias:
            mid=int(len(self.vbias)/2)
            meanval=Iavg[mid:len(self.vbias)].mean()
            maxval=max(Iavg[mid:len(self.vbias)])
            minval=min(Iavg[mid:len(self.vbias)])
        else:
            meanval=Iavg.mean()
            maxval=max(Iavg)
            minval=min(Iavg)
        spread=abs(maxval-minval)
        if spread<abs_amplitude_limit:
            is_good[TES_index]=False
            comment[TES_index]='current too low'
            continue
        
        # third filter: peak to peak amplitude
        rel_amplitude=abs(spread/meanval)
        if rel_amplitude<rel_amplitude_limit:
            is_good[TES_index]=False
            comment[TES_index]='current peak-to-peak to small'
            continue

        # fourth filter: do we find a valid turnover for the Vbias?
        found_turnover=False
        n_inflections_within_range=0
        for n in range(len(fit['inflection'])):
            V0=fit['inflection'][n]
            concavity=fit['concavity'][n]
            if (not V0==None) and V0>self.min_bias and V0<self.max_bias:
                n_inflections_within_range+=1
                if concavity>0:
                    found_turnover=True
                    turnover[TES_index]=V0
        if not found_turnover:
            is_good[TES_index]=False
            comment[TES_index]='no turnover'
            continue

        # fifth filter:  do we have both inflection points within the bias range?
        if n_inflections_within_range>1:
            is_good[TES_index]=False
            comment[TES_index]='bad I-V profile'
            continue

        # sixth filter: is the operational point (the turnover) within the acceptable range?
        if turnover[TES_index]<self.min_bias+bias_margin or turnover[TES_index]>self.max_bias-bias_margin:
            is_good[TES_index]=False
            comment[TES_index]='Vbias operation point outside acceptable range'
            continue
            

            
        # we only get this far if it's a good I-V
        good_index.append(TES_index)


    ret['offset']=I_offset
    ret['is_good']=is_good
    ret['good_index']=good_index
    ret['ngood']=len(good_index)
    ret['turnover']=turnover
    ret['comment']=comment
    self.filterinfo=ret
    return ret

def read_Vtes_file(self,filename):
    if not os.path.exists(filename):
        print("file not found: ",filename)
        return None

    # try to get date from filename
    self.obsdate=self.read_date_from_filename(filename)

    handle=open(filename,'r')
    raw=handle.read()
    handle.close()
    lines=raw.split('\n')
    nlines=0
    X=[]
    for line in lines:
        if line=='':
            continue
        nlines+=1
        line_list=line.split('\t')
        row=np.empty(len(line_list))
        i=0
        for strval in line_list:
            val=eval(strval)
            row[i]=val
            i+=1
        X.append(row)
        v_tes=np.array(X)
    self.assign_Vtes(v_tes)
    return v_tes

def make_iv_tex_report(self):
    thumbnailplot=str('TES_IV_ASIC%i_%s.png' % (self.asic,self.obsdate.strftime('%Y%m%dT%H%M%SUTC')))
    allplot=str('TES_IV_ASIC%i_all_%s.png' % (self.asic,self.obsdate.strftime('%Y%m%dT%H%M%SUTC')))
    pattern=str('TES???_IV_ASIC%i_%s.png' % (self.asic,self.obsdate.strftime('%Y%m%dT%H%M%SUTC')))
    iv_plots=glob(pattern)
    iv_plots.sort()

    observer=self.observer.replace('<','$<$').replace('>','$>$')
    
    texfilename=str('TES_IV_ASIC%i_%s.tex' % (self.asic,self.obsdate.strftime('%Y%m%dT%H%M%SUTC')))
    h=open(texfilename,'w')
    h.write('\\documentclass[a4paper,12pt]{article}\n')
    h.write('\\usepackage{graphicx}\n')
    h.write('\\usepackage{hyperref}\n')
    h.write('\\begin{document}\n')
    h.write('\\begin{center}\n')
    h.write('QUBIC TES Report\\\\\n')
    h.write(self.obsdate.strftime('data from %Y-%m-%d %H:%M UTC\\\\\n'))
    h.write('compiled by %s\\\\\nusing PyStudio/QubicPack: \\url{https://github.com/satorchi/pystudio}\n' % observer)
    h.write('\\end{center}\n')

    h.write('\\noindent Summary:\n')
    h.write('\\noindent\\begin{itemize}\n')
    h.write('\\item ASIC %i\n' % self.asic)
    h.write('\\item %i pixels are flagged as bad.\n\\item %.1f\\%s of the array is good\n'\
            % ( self.NPIXELS-self.filterinfo['ngood'], 100.0*self.filterinfo['ngood']/self.NPIXELS, '%' ))
    h.write('\\end{itemize}\n')
    
    h.write('\n\\vspace*{3ex}\n\\noindent This document includes the following:\n')
    h.write('\\begin{itemize}\n')
    h.write('\\item Table of turnover points for each TES\n')
    h.write('\\item Plot of all the I-V curves, each in its corresponding location in the focal plane\n')
    h.write('\\item Plot of all the good I-V curves on a single plot\n')
    h.write('\\item Plot of each TES I-V curve (%i plots)\n' % self.NPIXELS)
    h.write('\\end{itemize}\n\\clearpage\n')

    h.write('\\begin{table}[h]\n')
    h.write('\\caption{List of turnover (operation) points for each TES}\n')
    h.write('\\begin{tabular}{|r|r||||r|r||||r|r||||r|r|}\n')
    h.write('\\hline\n')
    ncols=4
    nrows=int(self.NPIXELS/ncols)
    for i in range(nrows):
        for j in range(ncols):
            if self.filterinfo['turnover'][i+j*nrows]==None:
                turnover='bad pixel'
            else:
                turnover=str('%.2f' % self.filterinfo['turnover'][i+j*nrows])
            h.write('%3i & %s' % (i+1+j*nrows, turnover))
            if j<3: h.write(' &')
            else: h.write('\\\\\n')
    h.write('\\hline\n')
    h.write('\\end{tabular}\n')
    h.write('\\end{table}\n\\clearpage\n')
    
    h.write('\n\\includegraphics[width=0.8\\linewidth,clip]{%s}\\\\' % thumbnailplot)
    h.write('\n\\includegraphics[width=0.8\\linewidth,clip]{%s}\n\\clearpage\n' % allplot)
    for png in iv_plots:
        h.write('\n\\includegraphics[width=0.8\\linewidth,clip]{%s}\\\\' % png)

    
    
    h.write('\n\n\\end{document}\n')
    h.close()
    return


