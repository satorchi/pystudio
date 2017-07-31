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

def plot_iv_all(self,selection=None,xwin=True):
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
    if xwin: plt.ion()
    fig=plt.figure(figsize=self.figsize)
    if xwin: fig.canvas.set_window_title('plt: '+ttl) 
    fig.suptitle(ttl+'\n'+subttl,fontsize=16)
    plt.xlabel('Bias Voltage  /  V')
    plt.ylabel('Current  /  $\mu$A')

    nbias=self.v_tes.shape[1]
    
    offset=[]
    colour_idx=0
    ncolours=len(self.colours)
    for TES_index in range(self.NPIXELS):
        TES=TES_index+1

        if (selection==None) or (selection[TES_index]):
            if self.filterinfo==None:
                filterinfo=self.filter_iv(TES)
                offset=filterinfo['offset']
            else:
                offset=self.filterinfo['offset'][TES_index]

            Iadjusted=self.ADU2I(self.v_tes[TES_index,:],offset)

            if colour_idx >= ncolours:colour_idx=0
            self.draw_iv(Iadjusted,colour=self.colours[colour_idx])
            colour_idx+=1

    pngname=str('TES_IV_ASIC%i_all_%s.png' % (self.asic,self.obsdate.strftime('%Y%m%dT%H%M%SUTC')))
    plt.savefig(pngname,format='png',dpi=100,bbox_inches='tight')
    if xwin: plt.show()
    return fig

def setup_plot_iv_multi(self,nrows=16,ncols=8,xwin=True):
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
    
    if xwin: plt.ion()
    fig,axes=plt.subplots(nrows,ncols,sharex=True,sharey=False,figsize=self.figsize)
    if xwin: fig.canvas.set_window_title('plt: '+ttl)
    fig.suptitle(ttl,fontsize=16)
    plt.xlabel('Bias Voltage  /  V')
    plt.ylabel('Current  /  $\mu$A')
    return fig,axes

def plot_iv_multi(self, xwin=True):
    '''
    plot all TES I-V curves on a grid
    the optional list "is_good" is boolean for each TES
    if present, a label will be shown on each curve indicating 
    whether that TES is considered good or not
    '''
    if not self.filterinfo==None: ngood=self.filterinfo['ngood']
    nrows=16
    ncols=8
    fig,axes=self.setup_plot_iv_multi(nrows,ncols,xwin)
    
    TES_index=0
    for row in range(nrows):
        for col in range(ncols):
            TES=TES_index+1
            
            axes[row,col].get_xaxis().set_visible(False)
            axes[row,col].get_yaxis().set_visible(False)

            if self.filterinfo==None:
                filterinfo=self.filter_iv(TES)
                offset=filterinfo['offset']
            else:
                offset=self.filterinfo['offset'][TES_index]

            Iadjusted=self.ADU2I(self.v_tes[TES_index,:],offset)            
            self.draw_iv(Iadjusted,colour='blue',axis=axes[row,col])
            text_y=min(Iadjusted)
            axes[row,col].text(self.max_bias,text_y,str('%i' % (TES_index+1)),va='bottom',ha='right',color='black')

            if (not self.filterinfo==None)\
               and (not self.filterinfo['is_good']==None)\
               and (not self.filterinfo['is_good'][TES_index]):
                # axes[row,col].text(self.min_bias,text_y,'BAD',va='bottom',ha='left',color='red')
                axes[row,col].set_axis_bgcolor('red')

            TES_index+=1

    pngname=str('TES_IV_ASIC%i_thumbnail_%s.png' % (self.asic,self.obsdate.strftime('%Y%m%dT%H%M%SUTC')))
    plt.savefig(pngname,format='png',dpi=100,bbox_inches='tight')
    if xwin: plt.show()
    
    return fig

def plot_iv_physical_layout(self,xwin=True):
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

    if xwin: plt.ion()
    fig,ax=plt.subplots(nrows,ncols,figsize=self.figsize)
    subttl=str('ASIC #%i' % self.asic)
    if not ngood==None:
        subttl+=str(': %i flagged as bad pixels' % (self.NPIXELS-ngood))
    pngname=str('TES_IV_ASIC%i_%s.png' % (self.asic,self.obsdate.strftime('%Y%m%dT%H%M%SUTC')))
    if xwin: fig.canvas.set_window_title('plt:  '+ttl)
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

                if self.filterinfo==None:
                    filterinfo=self.filter_iv(TES)
                    offset=filterinfo['offset']
                else:
                    offset=self.filterinfo['offset'][TES_index]
                Iadjusted=self.ADU2I(self.v_tes[TES_index,:],offset)            
                text_y=min(Iadjusted)
                self.draw_iv(Iadjusted,colour='blue',axis=ax[row,col])

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
    if xwin: plt.show()

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

def draw_tangent(self,fit=None):
    '''
    make a tangent line of the I-V curve fit at the maximum bias
    '''
    if fit==None: return None,None

    # coefficients of the polyfit
    # we add the offset which moves the curve so that the equivalent circuit has R=1 Ohm at maximum Vbias 
    a3=fit['fitinfo'][0][0]
    a2=fit['fitinfo'][0][1]
    a1=fit['fitinfo'][0][2]
    a0=fit['fitinfo'][0][3] + fit['offset']

    # tangent is the first derivative of the polyfit
    R1=fit['R1']
    slope=1/R1
    
    V=self.vbias[self.max_bias_position]
    Imax=a0 + a1*V + a2*(V**2) + a3*(V**3)

    # The line is described by: y=slope*x + I0
    I0=Imax-slope*V

    V2=self.min_bias
    I2=slope*V2 + I0

    xpts=[V2,V]
    ypts=[I2,Imax]
    plt.plot(xpts,ypts,linestyle='dashed',color='green')
    
    return R1,I0

def filter_jumps(self,I,jumplimit=2.0):
    '''
    filter out big jumps and return the remaining curve for fitting
    '''
    self.debugmsg('filtering jumps')
    npts_curve=len(I)

    # find the step size between subsequent bias points
    # we make this relative to the lower point in the step
    # so that a big step is a big number
    steps=[]
    for idx in np.arange(1,npts_curve):
        stepsize=I[idx]-I[idx-1]
        if stepsize>self.zero:
            rel_stepsize = abs(stepsize/I[idx-1])
        elif stepsize<self.zero:
            rel_stepsize = abs(stepsize/I[idx])
        else:
            rel_stepsize=1/self.zero
        steps.append(rel_stepsize)
        self.debugmsg('%i) stepsize: %.4f' % (idx,rel_stepsize))
    steps=np.array(steps)

    # find big steps 
    xpts=[]
    # don't forget to include the first and last point!
    xpts.append(0)
    meanval=steps.mean()
    for idx in range(len(steps)):
        sigma=steps[idx]/meanval
        self.debugmsg('%i) sigma stepsize: %.4f' % (idx+1,sigma))
        if sigma>jumplimit: xpts.append(idx)
    xpts.append(npts_curve-1)
    msg=''
    for idx in xpts:
        msg=str('%s %i,' % (msg,idx))
    msg='found big jumps at: '+msg
    self.debugmsg(msg)
    # we will return the largest span of non-jump data found in the curve
    maxspan=0
    maxspan_idx1=0
    maxspan_idx2=npts_curve
    for idx in range(len(xpts)-1):
        idx_next=idx+1
        span=abs(xpts[idx_next]-xpts[idx])
        if span>maxspan:
            maxspan=span
            maxspan_idx1=xpts[idx]
            maxspan_idx2=xpts[idx_next]

    # we only return the indexes of the good span
    self.debugmsg('best span of points in the curve is %i:%i' % (maxspan_idx1,maxspan_idx2))
    return maxspan_idx1,maxspan_idx2

def fit_iv(self,TES,jumplimit=2.0):
    '''
    fit the I-V curve to a polynomial

    if we're cycling, we always go down-up-down or up-down-up for a single cycle
    so a single IV curve is 1/(2*ncycles)

    we work directly with the uncalibrated data.
    The fit will be used to make the final adjustments
    '''
    
    TES_index=self.TES_index(TES)
    
    # a small number
    zero=self.zero
    
    # return is a dictionary with various info
    ret={}

    I=self.ADU2I(self.v_tes[TES_index,:])
    npts=len(I)

    if self.cycle_vbias:
        ncurves=self.nbiascycles*2
    else:
        ncurves=self.nbiascycles
    npts_curve=int(npts/ncurves)
    ret['ncurves']=ncurves
    ret['npts_curve']=npts_curve
    self.debugmsg('number of curves: %i' % ncurves)
    self.debugmsg('npts per curve: %i' % npts_curve)
    
    # fit for each measured curve and find the best one
    best_residual=1./zero
    best_curve_index=0
    allfits=[]
    istart=0
    for idx in range(ncurves):
        iend=istart+npts_curve
        ypts=I[istart:iend]
        self.debugmsg('cycle %i: fitting curve istart=%i, iend=%i' % ((idx+1),istart,iend))
        xpts=self.vbias[istart:iend]

        # filter out the big jumps
        # the return is the range of indexes of the acceptable points
        good_start,good_end=self.filter_jumps(ypts,jumplimit)
        npts_span=good_end-good_start
        if npts_span<5:
            self.debugmsg('couldn\'t find a large span without jumps! Fitting the whole curve...')
            good_start=0
            good_end=len(xpts)
            npts_span=npts_curve
        curve=ypts[good_start:good_end]
        bias=xpts[good_start:good_end]
        
        # fit to polynomial degree 3
        # normalize the residual to the number of points in the fit
        fit=np.polyfit(bias,curve,3,full=True)
        residual=fit[1][0]/npts_span
        allfits.append(fit)
        if abs(residual)<best_residual:
            best_residual=abs(residual)
            best_curve_index=idx
        istart+=npts_curve

    # from now on we use the best curve fit
    ret['best curve index']=best_curve_index
    fitinfo=allfits[best_curve_index]
    ret['fitinfo']=fitinfo
    
    # the coefficients of the polynomial fit
    a3=fitinfo[0][0]
    a2=fitinfo[0][1]
    a1=fitinfo[0][2]
    a0=fitinfo[0][3]

    # we shift the fit curve up/down to have I(max_bias)=max_bias
    #   which puts the max bias position at a point on the R=1 Ohm line
    V=self.vbias[self.max_bias_position]
    Imax=a0 + a1*V + a2*(V**2) + a3*(V**3)
    offset=V-Imax
    ret['offset']=offset
    
    # find the tangent line of the fit to the I-V curve at the maximum bias
    # this should be equivalent to a circuit with resistance 1 Ohm
    # tangent is the first derivative of the polyfit
    slope=a1 + 2*a2*V + 3*a3*(V**2)
        
    # The line should have a slope equal to a circuit with resistance 1 Ohm
    if abs(slope)>zero:
        R1 = 1/slope
    else:
        R1=1/zero
    ret['R1']=R1

    # find turning where polynomial tangent is zero (i.e. first derivative is zero)
    ####### NOTE:  I don't think this is "inflection" ! I should change the word here.
    t1=-a2/(3*a3)
    discriminant=a2**2 - 3*a1*a3
    if discriminant<0.0:
        ret['turning']=[None,None]
        ret['concavity']=[None,None]
        return ret

    t2=math.sqrt(discriminant)/(3*a3)
    x0_0=t1+t2
    x0_1=t1-t2
    ret['turning']=[x0_0,x0_1]

    # check the concavity of the turning: up or down (+ve is up)
    ret['concavity']=[2*a2 + 6*a3*x0_0, 2*a2 + 6*a3*x0_1]
    
    keys=''
    for key in ret.keys():keys+=key+', '
    self.debugmsg('returning from fit_iv() with keys: %s' % keys)
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

def plot_iv(self,TES=None,offset=None,fudge=1.0,multi=False,jumplimit=2.0,xwin=True):
    if multi:return self.plot_iv_multi()
    if TES==None:return self.plot_iv_all()
    if not isinstance(TES,int): return self.plot_iv_all()

    TES_index=self.TES_index(TES)
    
    if self.vbias==None: self.vbias=make_Vbias()
    
    fig,ax=self.setup_plot_iv(TES,xwin)

    # normalize the Current so that R=1 Ohm at the highest Voffset
    fit=self.fit_iv(TES,jumplimit)
    offset=fit['offset']
    txt=str('offset=%.4e' % offset)

    
    Iadjusted=self.ADU2I(self.v_tes[TES_index,:],offset=offset,fudge=fudge)
    self.draw_iv(Iadjusted)

    # draw a polynomial fit to the I-V curve
    txt+=str('\npolynomial fit residual: %.4e' % fit['fitinfo'][1][0])
    f=np.poly1d(fit['fitinfo'][0]) + offset
    plt.plot(self.vbias,f(self.vbias),linestyle='dashed',color='red')

    # note the turnover point
    found_turnover=False
    for n in range(2):
        v0=fit['turning'][n]
        concavity=fit['concavity'][n]
        if (not v0==None) and v0>self.min_bias and v0<self.max_bias and concavity>0:
            xpts=[v0,v0]
            ypts=[min(Iadjusted),max(Iadjusted)]
            plt.plot(xpts,ypts,linestyle='dashed',color='green')
            found_turnover=True
            txt+=str('\nturnover Vbias=%.2fV' % v0)
    if not found_turnover:
        txt+='\nNo turnover!'
        
    
    # draw a line tangent to the fit at the highest Vbias
    R1,I0=self.draw_tangent(fit)
    if not R1==None: txt+=str('\ndynamic normal resistance:  R$_1$=%.4f $\Omega$' % R1)

    # use the filter if we've already run it, otherwise do it here
    if self.filterinfo==None:
        filterinfo=self.filter_iv(TES)
        is_good=filterinfo['is_good']
        comment=filterinfo['comment']
    else:
        is_good=self.filterinfo['is_good'][TES_index]
        comment=self.filterinfo['comment'][TES_index]
    if not is_good:
        txt+=str('\nFlagged as BAD:  %s' % comment)
    # write out the comments
    text_x=self.min_bias + 0.95*(self.max_bias-self.min_bias)
    text_y=min(Iadjusted) + 0.98*(max(Iadjusted)-min(Iadjusted))
    plt.text(text_x,text_y,txt,va='top',ha='right',fontsize=12)
    pngname=str('TES%03i_IV_ASIC%i_%s.png' % (TES,self.asic,self.obsdate.strftime('%Y%m%dT%H%M%SUTC')))
    plt.savefig(pngname,format='png',dpi=100,bbox_inches='tight')
    if xwin:
        plt.show()
    else:
        plt.clf()
        plt.close(fig.number)
    return fig

def make_Vbias(self,cycle=True,ncycles=2,vmin=5.0,vmax=9.0,dv=0.04,lowhigh=True):
    '''
    the bias voltage values used during the I-V curve measurement
    '''

    if ncycles<1:
        print('Please enter a number of cycles greater than 0!')
        return None
    
    going_up=np.arange(vmin,vmax+dv,dv)
    going_dn=np.flip(going_up,0)

    if cycle:
        if lowhigh:
            onecycle=np.concatenate((going_up,going_dn),0)
        else:
            onecycle=np.concatenate((going_dn,going_up),0)
    else:
        if lowhigh:
            onecycle=going_up
        else:
            onecycle=going_dn

    self.cycle_vbias=cycle
    self.nbiascycles=ncycles
    self.min_bias=min(self.vbias)
    self.max_bias=max(self.vbias)
    self.max_bias_position=np.argmax(self.vbias)

    vbias=onecycle
    for n in range(ncycles-1):
        vbias=np.concatenate((vbias,onecycle),0)
    
    self.vbias=vbias
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

def get_iv_data(self,replay=False,TES=None,monitor=False):
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
            Iadjusted=self.ADU2I(I_tes)
            self.draw_iv(Iadjusted,axis=axiv)

        if monitor:
            # monitor all the I-V curves:  Warning!  Extremely slow!!!
            TES_index=0
            for row in range(nrows):
                for col in range(ncols):
                    axmulti[row,col].get_xaxis().set_visible(False)
                    axmulti[row,col].get_yaxis().set_visible(False)

                    Iadjusted=self.ADU2I(self.v_tes[TES_index,0:j+1])
                    self.draw_iv(Iadjusted,colour='blue',axis=axmulti[row,col])
                    text_y=min(Iadjusted)
                    axmulti[row,col].text(max(self.vbias),text_y,str('%i' % (TES_index+1)),va='bottom',ha='right',color='black')
            
                    TES_index+=1
        


    plt.show()
    self.assign_Vtes(v_tes)
    if not replay:
        self.write_fits()
    
    return v_tes

def filter_iv(self,TES,residual_limit=3.0,abs_amplitude_limit=0.01,rel_amplitude_limit=0.1,bias_margin=0.2,jumplimit=2.0):
    '''
    determine if this is a good TES from the I-V curve
    '''
    TES_index=self.TES_index()
    
    # dictionary to return stuff
    ret={}
    ret['is_good']=True
    ret['comment']='no comment'
    ret['turnover']=None

    # fit to a polynomial. The fit will be for the best measured curve if it's cycled bias
    fit=self.fit_iv(TES,jumplimit)
    ret['fit']=fit
    residual=fit['fitinfo'][1][0]
    ret['residual']=residual
    offset=fit['offset']
    ret['offset']=offset
    Iadjusted=self.ADU2I(self.v_tes[TES_index,:],offset=offset)

    # first filter:  is it a good fit?
    if residual>residual_limit:
        ret['is_good']=False
        ret['comment']='bad poly fit'
        return ret
    
    # second filter: small amplitude is rejected
    # best curve is determined by the fit
    npts=fit['npts_curve']
    istart=npts*fit['best curve index']
    iend=npts*(fit['best curve index']+1)
    meanval=Iadjusted[istart:iend].mean()
    maxval=max(Iadjusted[istart:iend])
    minval=min(Iadjusted[istart:iend])
    spread=abs(maxval-minval)
    if spread<abs_amplitude_limit:
        ret['is_good']=False
        ret['comment']='current too low'
        return ret
        
    # third filter: peak to peak amplitude
    rel_amplitude=abs(spread/meanval)
    if rel_amplitude<rel_amplitude_limit:
        ret['is_good']=False
        ret['comment']='current peak-to-peak to small'
        return ret
    
    # fourth filter: do we find a valid turnover for the Vbias?
    found_turnover=False
    n_turnings_within_range=0
    for n in range(len(fit['turning'])):
        V0=fit['turning'][n]
        concavity=fit['concavity'][n]
        if (not V0==None) and V0>self.min_bias and V0<self.max_bias:
            n_turnings_within_range+=1
            if concavity>0:
                found_turnover=True
                ret['turnover']=V0
    if not found_turnover:
        ret['is_good']=False
        ret['comment']='no turnover'
        return ret

    # fifth filter:  do we have both turning points within the bias range?
    if n_turnings_within_range>1:
        ret['is_good']=False
        ret['comment']='bad I-V profile'
        return ret
    
    # sixth filter: is the operational point (the turnover) within the acceptable range?
    if ret['turnover']<self.min_bias+bias_margin or ret['turnover']>self.max_bias-bias_margin:
        ret['is_good']=False
        ret['comment']='Vbias operation point outside acceptable range'
        return ret
    
    # we only get this far if it's a good I-V
    return ret

def filter_iv_all(self,residual_limit=3.0,abs_amplitude_limit=0.01,rel_amplitude_limit=0.1,bias_margin=0.2,jumplimit=2.0):
    '''
    find which TES are good
    '''
    if self.v_tes==None:
        print('No data!  Please read a file, or run a measurement.')
        return None

    # return a list with the filter info for each, and a list of the good indexes
    ret={}

    fitinfo=[]
    offset=[]
    is_good=[]
    turnover=[]
    comment=[]    

    # go through each filter.  Jump out and examine the next I-V curve as soon as a bad I-V is found
    good_index=[]
    for TES_index in range(self.NPIXELS):
        self.debugmsg('running filter on TES %03i' % (TES_index+1))
        filterinfo=self.filter_iv(TES_index+1,residual_limit,abs_amplitude_limit,rel_amplitude_limit,bias_margin,jumplimit)
        if filterinfo['is_good']:good_index.append(TES_index)
        
        fitinfo.append(filterinfo['fit'])
        offset.append(filterinfo['offset'])
        is_good.append(filterinfo['is_good'])
        turnover.append(filterinfo['turnover'])
        comment.append(filterinfo['comment'])

        
    # these are recopied to a 'higher level' for historic compatibility.
    # eventually I should fix all the methods which rely on this
    ret['fitinfo']=fitinfo
    ret['offset']=offset
    ret['is_good']=is_good
    ret['turnover']=turnover
    ret['comment']=comment
    ret['good_index']=good_index
    ret['ngood']=len(good_index)
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
    '''
    make a report in LaTeX.  
    This relies on the data in self.filterinfo.  See self.filter_iv_all() above
    '''
    if self.filterinfo==None:
        print('Please run filter_iv_all() first!')
        return None
    
    thumbnailplot=str('TES_IV_ASIC%i_%s.png' % (self.asic,self.obsdate.strftime('%Y%m%dT%H%M%SUTC')))
    allplot=str('TES_IV_ASIC%i_all_%s.png' % (self.asic,self.obsdate.strftime('%Y%m%dT%H%M%SUTC')))
    pattern=str('TES???_IV_ASIC%i_%s.png' % (self.asic,self.obsdate.strftime('%Y%m%dT%H%M%SUTC')))
    iv_plots=glob(pattern)
    iv_plots.sort()

    if len(iv_plots)<self.NPIXELS:
        print('WARNING: Did not find all the I-V plots!')

    observer=self.observer.replace('<','$<$').replace('>','$>$')
    
    texfilename=str('TES_IV_ASIC%i_%s.tex' % (self.asic,self.obsdate.strftime('%Y%m%dT%H%M%SUTC')))
    h=open(texfilename,'w')
    h.write('\\documentclass[a4paper,12pt]{article}\n')
    h.write('\\usepackage{graphicx}\n')
    h.write('\\usepackage{hyperref}\n')
    h.write('\\usepackage{longtable}\n')
    h.write('\\begin{document}\n')
    h.write('\\begin{center}\n')
    h.write('QUBIC TES Report\\\\\n')
    h.write(self.obsdate.strftime('data from %Y-%m-%d %H:%M UTC\\\\\n'))
    h.write('compiled by %s\\\\\nusing PyStudio/QubicPack: \\url{https://github.com/satorchi/pystudio}\n' % observer)
    h.write(dt.datetime.utcnow().strftime('this report compiled %Y-%m-%d %H:%M UTC\\\\\n'))
    h.write('\\end{center}\n')

    h.write('\\vspace*{3ex}\n')
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

    ncols=1
    nrows=int(self.NPIXELS/ncols)
    colfmt='|r|r|r|l|'
    headline1='\\multicolumn{1}{|c|}{pix} & \\multicolumn{1}{c|}{V$_{\\rm turnover}$} & \\multicolumn{1}{c|}{R$_1$} & \\multicolumn{1}{c|}{comment}'
    headline=''
    headline+=headline1
    if ncols>1:
        for j in range(ncols-1):
            colfmt+='|||r|r|'
            headline+=' & '+headline1 
    h.write('\\noindent\\begin{longtable}{%s}\n' % colfmt)
    h.write('\\caption{List of turnover (operation) points for each TES}\\\\\n')
    # h.write('\\begin{tabular}{%s}\n' % colfmt)
    h.write('\\hline\n')
    h.write(headline+'\\\\ \n')
    h.write('\\hline\\endhead\n')
    h.write('\\hline\\endfoot\n')
    for i in range(nrows):
        for j in range(ncols):
            TES_index=i+j*nrows
            if self.filterinfo['turnover'][TES_index]==None:
                turnover='-'
            else:
                turnover=str('%.2f' % self.filterinfo['turnover'][TES_index])
            R1=self.filterinfo['fitinfo'][TES_index]['R1']
            if R1>1000:
                R1str='-'
            else:
                R1str=str('%.2f' % R1)
            comment=self.filterinfo['comment'][TES_index]
            if comment=='no comment': comment='good'
            h.write('%3i & %s & %s & %s' % (TES_index+1, turnover, R1str, comment))
            if j<ncols-1: h.write(' &')
            else: h.write('\\\\\n')
    h.write('\\hline\n')
    # h.write('\\end{tabular}\n')
    h.write('\\end{longtable}\n\\clearpage\n')
    
    h.write('\n\\noindent\\includegraphics[width=0.8\\linewidth,clip]{%s}\\\\' % thumbnailplot)
    h.write('\n\\includegraphics[width=0.8\\linewidth,clip]{%s}\n\\clearpage\n\\noindent' % allplot)
    for png in iv_plots:
        h.write('\n\\includegraphics[width=0.8\\linewidth,clip]{%s}\\\\' % png)

    
    
    h.write('\n\n\\end{document}\n')
    h.close()
    return texfilename


def make_iv_report(self):
    '''
    do all the business to generate the I-V report document
    '''

    # run filter
    self.filter_iv_all()

    # plot all the I-V in the focal-plane map
    self.figsize=(14,14)
    self.plot_iv_physical_layout(xwin=False)

    # plot all the good I-V curves on a single plot
    self.plot_iv_all(selection=self.filterinfo['is_good'],xwin=False)

    # plot each I-V curve
    self.figsize=(16,12)
    for TES_index in range(self.NPIXELS):
        self.plot_iv(TES_index+1,xwin=False)

    # generate the LaTeX file
    texname=self.make_iv_tex_report()

    # process the LaTeX file a couple of times
    cmd='pdflatex %s' % texname
    os.system(cmd)
    os.system(cmd)
    return

    
