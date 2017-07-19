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
    I = 1e6 * (ADU / 2**7) * (q_ADC/G_FLL) * fudge

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
    min_bias=min(self.vbias)
    max_bias=max(self.vbias)
    if isinstance(self.obsdate,dt.datetime):
        ttl=str('QUBIC I-V curves (%s)' % (self.obsdate.strftime('%Y-%b-%d %H:%M UTC')))
    else:
        ttl=str('QUBIC I-V curve per TES with Vbias ranging from %.2fV to %.2fV' % (min_bias,max_bias))
    if selection != None:
        nselection=0
        for val in selection:
            if val: nselection+=1
    else:
        nselection=self.NPIXELS
                
    subttl=str('plotting curves for %i TES out of %i' % (nselection,self.NPIXELS))
    plt.ioff()
    fig=plt.figure(figsize=self.figsize)
    fig.canvas.set_window_title('plt: '+ttl) 
    fig.suptitle(ttl,fontsize=16)
    plt.title(subttl,fontsize=14)
    plt.xlabel('Bias Voltage  /  V')
    plt.ylabel('Current  /  $\mu$A')

    nbias=self.v_tes.shape[1]
    Ntes=self.v_tes.shape[0]

    max_bias=max(self.vbias)
    max_bias_position=np.argmax(self.vbias)
    
    offset=[]
    colour_idx=0
    ncolours=len(self.colours)
    for n in range(Ntes):

        if (selection==None) or (selection[n]):
            I=self.ADU2I(self.v_tes[n,max_bias_position])
            # offset the Current so that R=1 Ohm at the highest Vbias
            offset=self.find_offset(I,max_bias)
            
            Iavg=self.ADU2I(self.v_tes[n,:],offset)

            if colour_idx >= ncolours:colour_idx=0
            self.draw_iv(Iavg,colour=self.colours[colour_idx])
            colour_idx+=1

    pngname='I-V_all.png'
    plt.savefig(pngname,format='png',dpi=100,bbox_inches='tight')
    plt.show()
    return fig

def plot_iv_multi(self):
    if self.vbias==None: self.vbias=make_Vbias()
    min_bias=min(self.vbias)
    max_bias=max(self.vbias)
    max_bias_position=np.argmax(self.vbias)
    if isinstance(self.obsdate,dt.datetime):
        ttl=str('QUBIC I-V curves (%s)' % (self.obsdate.strftime('%Y-%b-%d %H:%M UTC')))
    else:
        ttl=str('QUBIC I-V curve per TES with Vbias ranging from %.2fV to %.2fV' % (min_bias,max_bias))

    nrows=16
    ncols=8
    plt.ion()
    fig,axes=plt.subplots(nrows,ncols,sharex=True,sharey=False,figsize=self.figsize)
    fig.canvas.set_window_title('plt: '+ttl)
    fig.suptitle(ttl,fontsize=16)
    plt.xlabel('Bias Voltage  /  V')
    plt.ylabel('Current  /  $\mu$A')

    tes_index=0
    for row in range(nrows):
        for col in range(ncols):
            axes[row,col].get_xaxis().set_visible(False)
            axes[row,col].get_yaxis().set_visible(False)

            I=self.ADU2I(self.v_tes[tes_index,max_bias_position])
            # offset the Current so that R=1 Ohm at the highest Vbias
            offset=self.find_offset(I,max_bias)
            Iavg=self.ADU2I(self.v_tes[tes_index,:],offset)            
            self.draw_iv(Iavg,colour='blue',axis=axes[row,col])
            # axes[row,col].plot(self.vbias,Iavg,color='blue')
            text_y=min(Iavg)
            axes[row,col].text(max_bias,text_y,str('%i' % (tes_index+1)),va='bottom',ha='right',color='black')
            
            tes_index+=1

    pngname='I-V_all_multi.png'
    plt.savefig(pngname,format='png',dpi=100,bbox_inches='tight')
    plt.show()
    
    return fig

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
    fit the I-V curve to a parabola
    '''
    if self.cycle_vbias:
        # only fit half the points
        mid=int(len(self.vbias)/2)
        ypts=I[0:mid]
        xpts=self.vbias[0:mid]
        npts=len(xpts)
    else:
        ypts=I
        xpts=self.vbias
        npts=len(I)

    ret=np.polyfit(xpts,ypts,2,full=True)
    return ret

def draw_iv(self,I,colour='blue',axis=plt):
    '''
    draw an individual I-V curve
    '''
    if self.cycle_vbias:
        # plot down and up voltage with different linestyles
        mid=int(len(self.vbias)/2)
        axis.plot(self.vbias[0:mid],I[0:mid],linestyle='solid', color=colour)
        axis.plot(self.vbias[mid:-1], I[mid:-1], linestyle='dashed',color=colour)
    else:
        axis.plot(self.vbias,I,color=colour)
    return

def plot_iv(self,TES=None,offset=None,fudge=1.0,multi=False):
    if multi:return self.plot_iv_multi()
    if TES==None:return self.plot_iv_all()
    if not isinstance(TES,int): return self.plot_iv_all()

    TES_index=self.TES_index(TES)
    
    
    if self.vbias==None: self.vbias=make_Vbias()
    min_bias=min(self.vbias)
    max_bias=max(self.vbias)
    max_bias_position=np.argmax(self.vbias)
    
    # normalize the Current so that R=1 Ohm at the highest Voffset
    Vbias=self.vbias[max_bias_position]
    I=self.ADU2I(self.v_tes[TES_index,max_bias_position])
    if offset==None: offset=self.find_offset(I,Vbias)

    if isinstance(self.obsdate,dt.datetime):
        ttl=str('QUBIC I-V curve for TES#%3i (%s)' % (TES,self.obsdate.strftime('%Y-%b-%d %H:%M UTC')))
    else:
        ttl=str('QUBIC I-V curve for TES#%3i with Vbias ranging from %.2fV to %.2fV' % (TES,min_bias,max_bias))
    subttl=str('offset I=%.4e' % offset)
    plt.ion()
    fig=plt.figure(figsize=self.figsize)
    fig.canvas.set_window_title('plt: '+ttl) 
    fig.suptitle(ttl,fontsize=16)
    plt.title(subttl)
    plt.xlabel('Bias Voltage  /  V')
    plt.ylabel('Current  /  $\mu$A')

    Iavg=self.ADU2I(self.v_tes[TES_index,:],offset=offset,fudge=fudge)
    self.draw_iv(Iavg)

    # draw a polynomial fit to the I-V curve
    fit=self.fit_iv(Iavg)
    fitinfo=str('polynomial fit residual: %.4e' % fit[1][0])
    print(fitinfo)
    f=np.poly1d(fit[0])
    plt.plot(self.vbias,f(self.vbias),linestyle='dashed',color='red')
    text_x=min_bias + 0.5*(max_bias-min_bias)
    text_y=min(Iavg) + 0.8*(max(Iavg)-min(Iavg))
    plt.text(text_x,text_y,fitinfo,fontsize=14,horizontalalignment='center')
    
    # draw a line tangent to the final points
    I1=self.ADU2I(self.v_tes[TES_index,max_bias_position],offset=offset,fudge=fudge)
    bias1=max_bias
    pos2=max_bias_position-2
    if pos2<0: pos2=max_bias_position+2
        
    bias2=self.vbias[pos2]
    I2=self.ADU2I(self.v_tes[TES_index,pos2],offset=offset,fudge=fudge)
    pt1=[bias1,I1]
    pt2=[bias2,I2]
    I_R1=self.make_line(pt1,pt2,min_bias,max_bias)
    plt.plot([min_bias,max_bias],I_R1,linestyle='dashed',color='green')

    pngname=str('IV_TES%0i.png' % TES)
    plt.show()
    plt.savefig(pngname,format='png',dpi=100,bbox_inches='tight')
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
    return vbias

def get_Vavg_data(self):
    client = self.connect_QubicStudio()
    if client==None: return None

    ofilename = dt.datetime.utcnow().strftime("test_vi_%Y%m%dT%H%M%SUTC.txt")

    if self.vbias==None: vbias=make_Vbias()
    nbias=len(vbias)

    v_tes = np.empty((self.NPIXELS,nbias))

    fig=setup_plot_Vavg()
    for j in range(nbias) :
        print("measures at Voffset=%gV " % vbias[j])
        self.set_VoffsetTES(vbias[j],0.0,self.asic_index())
        wait_a_bit(0.3)
        Vavg= self.get_mean(tinteg,asic)
        print ("a sample of V averages :  %g %g %g " %(Vavg[0], Vavg[43], Vavg[73]) )
        v_tes[:,j]=Vavg
        plot_Vavg(Vavg,vbias[j])


    plt.show()
    np.savetxt(ofilename, v_tes,delimiter="\t")
    self.assign_Vtes(v_tes)
    return v_tes

def filter_Vtes(self):
    means=self.v_tes.mean(axis=1)
    meanmean_all=means.mean()
    good=[]

    # first filter: get rid of negative values
    # and also large values
    # recalulate meanmean of only the accepted traces
    meanmean=0.0
    ngood=0
    for val in means:
        if val<0.0 or (val>5*meanmean_all):
            good.append(False)
        else:
            good.append(True)
            meanmean+=val
            ngood+=1

    if ngood==0:
        print("all TES are bad!!")
        return good
    meanmean=meanmean/ngood


    # second filter: reject large means
    #for i in range(self.NPIXELS):
    #    if good[i] and (means[i] > 5 * meanmean): good[i]=False

    ngood=0
    good_index=[]
    good_mean=[]
    for val in good:
        if val:
            good_index.append(ngood)
            good_mean.append(means[ngood])
            ngood+=1
    
    return good, good_index, good_mean


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

def heres_one_I_made_earlier(self,filename=None, axes=None):
    '''
    loop through a saved file as if it's a real time measurement
    '''
    if filename==None:
        flist=glob('test_vi*')
        if len(flist)>0:
            filename=flist[0]            
    
    v_tes=self.read_Vtes_file(filename)
    if v_tes==None:return None

    if self.vbias==None: vbias=make_Vbias()

    nTES=v_tes.shape[0]
    nbias=v_tes.shape[1]

    # offset the Current so that R=1 Ohm at the highest Vbias
    max_bias=max(vbias)
    max_bias_position=np.argmax(vbias)
    
    offset=[]
    for TES in range(nTES):
        I=self.ADU2I(v_tes[TES,max_bias_position])
        offset_TES=self.find_offset(I,max_bias)
        offset.append(offset_TES)
        I_offset[TES,:]=self.ADU2I(v_tes[TES,:], offset=offset_TES)


    # try to find reasonable axes: 5sigma to cut off outliers
    # this can be overrode by the axes keyword
    sigma=I_offset.std()
    I_mean=I_offset.mean()
    iv_axes=[-1,self.NPIXELS,I_mean-5*sigma,I_mean+5*sigma]
    if axes==None:axes=self.iv_axes
    fig=self.setup_plot_Vavg(axes=axes)
    
    for j in range(nbias) :
        print("measures at Voffset=%gV " % vbias[j])
        
        ADUavg = v_tes[:,j] 
        print ("a sample of ADU averages :  %g %g %g " %(ADUavg[0], ADUavg[43], ADUavg[73]) )        
        self.plot_Vavg(ADUavg,vbias[j],offset,axes)
    
    plt.show()            
    return v_tes

