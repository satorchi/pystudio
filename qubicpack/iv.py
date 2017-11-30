#!/usr/bin/env python
"""
$Id: iv.py

$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
$created: Wed 05 Jul 2017 14:39:42 CEST
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

methods to plot and analyse I-V curves

"""
from __future__ import division, print_function
import numpy as np
import sys,os,time
import datetime as dt
import matplotlib.pyplot as plt
from glob import glob
import math
import pickle
from scipy.optimize import curve_fit

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
    if isinstance(axes,list) or isinstance(axes,np.ndarray): plt.axis(axes)
    plt.xlabel('TES number')
    plt.ylabel('I  /  $\mu$A')
    return fig

def plot_Vavg(self,Vavg,Vbias,offset=None,axes=None):
    Iavg=self.ADU2I(Vavg,offset)
    
    lbl=str('V$_{bias}$ = %.2fV' % Vbias)
    plt.cla()
    if isinstance(axes,list) or isinstance(axes,np.ndarray): plt.axis(axes)
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
    if not isinstance(self.vbias,np.ndarray):
        self.vbias=make_Vbias()
    if isinstance(self.obsdate,dt.datetime):
        ttl=str('QUBIC I-V curves (%s)' % (self.obsdate.strftime('%Y-%b-%d %H:%M UTC')))
    else:
        ttl=str('QUBIC I-V curve per TES with Vbias ranging from %.2fV to %.2fV' % (self.min_bias,self.max_bias))
    if isinstance(selection,list):
        nselection=0
        for val in selection:
            if val: nselection+=1
    else:
        nselection=self.NPIXELS
                
    subttl=str('plotting curves for %i TES out of %i' % (nselection,self.NPIXELS))
    if xwin: plt.ion()
    else: plt.ioff()
    fig=plt.figure(figsize=self.figsize)
    if xwin: fig.canvas.set_window_title('plt: '+ttl) 
    fig.suptitle(ttl+'\n'+subttl,fontsize=16)
    plt.xlabel('Bias Voltage  /  V')
    plt.ylabel('Current  /  $\mu$A')

    nbias=self.adu.shape[1]
    
    offset=[]
    colour_idx=0
    ncolours=len(self.colours)
    for TES_index in range(self.NPIXELS):
        TES=TES_index+1

        if (not isinstance(selection,list)) or (selection[TES_index]):
            istart,iend=self.selected_iv_curve(TES)
            Iadjusted=self.adjusted_iv(TES)[istart:iend]
            bias=self.vbias[istart:iend]
            if colour_idx >= ncolours:colour_idx=0
            plt.plot(bias,Iadjusted,color=self.colours[colour_idx])
            colour_idx+=1

    pngname=str('TES_IV_array-%s_ASIC%i_all_%s.png' % (self.detector_name,self.asic,self.obsdate.strftime('%Y%m%dT%H%M%SUTC')))
    pngname_fullpath=self.output_filename(pngname)
    if isinstance(pngname_fullpath,str): plt.savefig(pngname_fullpath,format='png',dpi=100,bbox_inches='tight')
    if xwin: plt.show()
    else: plt.close('all')
    return fig

def setup_plot_iv_multi(self,nrows=16,ncols=8,xwin=True):
    if not isinstance(self.vbias,np.ndarray): self.vbias=make_Vbias()
    if isinstance(self.obsdate,dt.datetime):
        ttl=str('QUBIC I-V curves (%s)' % (self.obsdate.strftime('%Y-%b-%d %H:%M UTC')))
    else:
        ttl=str('QUBIC I-V curve per TES with Vbias ranging from %.2fV to %.2fV' % (self.min_bias,self.max_bias))

    nbad=0
    for val in self.is_good_iv():
        if not val:nbad+=1
    ttl+=str('\n%i flagged as bad pixels' % nbad)
    
    if xwin: plt.ion()
    else: plt.ioff()
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
    ngood=self.ngood()
    nrows=16
    ncols=8
    fig,axes=self.setup_plot_iv_multi(nrows,ncols,xwin)
    
    TES_index=0
    for row in range(nrows):
        for col in range(ncols):
            TES=TES_index+1
            
            axes[row,col].get_xaxis().set_visible(False)
            axes[row,col].get_yaxis().set_visible(False)

            Iadjusted=self.adjusted_iv(TES)
            self.draw_iv(Iadjusted,colour='blue',axis=axes[row,col])
            text_y=min(Iadjusted)
            axes[row,col].text(self.max_bias,text_y,str('%i' % (TES_index+1)),va='bottom',ha='right',color='black')

            if (not self.is_good_iv()==None)\
               and (not self.is_good_iv()[TES_index]):
                # axes[row,col].text(self.min_bias,text_y,'BAD',va='bottom',ha='left',color='red')
                axes[row,col].set_facecolor('red')

            TES_index+=1

    pngname=str('TES_IV_array-%s_ASIC%i_thumbnail_%s.png' % (self.detector_name,self.asic,self.obsdate.strftime('%Y%m%dT%H%M%SUTC')))
    pngname_fullpath=self.output_filename(pngname)
    if isinstance(pngname_fullpath,str): plt.savefig(pngname_fullpath,format='png',dpi=100,bbox_inches='tight')
    if xwin: plt.show()
    else: plt.close('all')
    
    return fig

def plot_iv_physical_layout(self,xwin=True):
    '''
    plot the I-V curves in thumbnails mapped to the physical location of each detector
    '''
    if not isinstance(self.adu,np.ndarray):
        print('ERROR! No data!')
        return None
    
    ttl=str('QUBIC I-V curves (%s)' % (self.obsdate.strftime('%Y-%b-%d %H:%M UTC')))

    ngood=self.ngood()
    nrows=self.pix_grid.shape[0]
    ncols=self.pix_grid.shape[1]

    if xwin: plt.ion()
    else: plt.ioff()
    fig,ax=plt.subplots(nrows,ncols,figsize=self.figsize)
    subttl=str('Array %s, ASIC #%i' % (self.detector_name,self.asic))
    if not self.temperature==None:
        subttl+=', T$_\mathrm{bath}$=%.2f mK' % (1000*self.temperature)
    if not ngood==None:
        subttl+=str(': %i flagged as bad pixels' % (self.NPIXELS-ngood))
    pngname=str('TES_IV_array-%s_ASIC%i_%s.png' % (self.detector_name,self.asic,self.obsdate.strftime('%Y%m%dT%H%M%SUTC')))
    pngname_fullpath=self.output_filename(pngname)
    if xwin: fig.canvas.set_window_title('plt:  '+ttl)
    fig.suptitle(ttl+'\n'+subttl,fontsize=16)
    

    # the pixel number is between 1 and 248
    TES_translation_table=self.TES2PIX[self.asic_index()]

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
                label_colour='black'
                face_colour='black'
            elif physpix in TES_translation_table:
                TES=self.pix2tes(physpix)
                pix_label=str('%i' % TES)
                label_colour='black'
                face_colour='white'
                TES_index=self.TES_index(TES)
                Iadjusted=self.adjusted_iv(TES)
                text_y=min(Iadjusted)
                self.draw_iv(Iadjusted,colour='blue',axis=ax[row,col])

                if (not self.is_good_iv(TES)==None) and (not self.is_good_iv(TES)):
                    face_colour='red'
                    label_colour='white'
                    # ax[row,col].text(self.min_bias,text_y,'BAD',va='bottom',ha='left',color=label_colour)
            else:
                pix_label='other\nASIC'
                label_colour='yellow'
                face_colour='blue'
                
            ax[row,col].set_facecolor(face_colour)
            ax[row,col].text(self.max_bias,text_y,pix_label,va='bottom',ha='right',color=label_colour,fontsize=8)
            
    if isinstance(pngname_fullpath,str): plt.savefig(pngname_fullpath,format='png',dpi=100,bbox_inches='tight')
    if xwin: plt.show()
    else: plt.close('all')

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

def draw_tangent(self,TES):
    '''
    make a tangent line of the I-V curve fit at the maximum bias
    '''
    R1=self.R1(TES)
    if R1==None: return None,None

    offset=self.offset(TES)
    
    # tangent is determined by the fit
    slope=1/R1
    
    V=self.bias_factor*self.max_bias
    Imax=V

    # The line is described by: y=slope*x + I0 + offset
    I0=Imax - slope*V - offset

    V2=self.bias_factor*self.min_bias
    I2=slope*V2 + I0 + offset

    xpts=[V2,V]
    ypts=[I2,Imax]
    plt.plot(xpts,ypts,linestyle='dashed',color='green')
    
    return R1,I0

def fitted_iv_curve(self,TES):
    '''
    make a curve from the fit parameters
    '''
    filterinfo=self.filterinfo(TES)
    if filterinfo==None:return None

    offset=self.offset(TES)

    fit=filterinfo['fit']

    istart,iend=self.selected_iv_curve(TES)
    bias=self.bias_factor*self.vbias[istart:iend]

    # polynomial fit
    if 'fitfunction' not in fit.keys() or fit['fitfunction']=='POLYNOMIAL':
        func=np.poly1d(fit['fitinfo'][0]) + offset
        f=func(bias)
        return bias,f

    # combined polynomial fit
    Vturnover,Vnormal,a0,a1,a2,b0,b1,b2,c0,c1=fit['fitinfo'][0]
    f=self.iv_function(bias,Vturnover,Vnormal,a0,a1,a2,b0,b1,b2,c0,c1) + offset
    return bias,f

def filter_jumps(self,I,jumplimit=2.0):
    '''
    filter out big jumps and return the remaining curve for fitting
    '''
    self.debugmsg('filtering jumps')
    npts_curve=len(I)

    # don't do anything if jumplimit not given
    if not (isinstance(jumplimit,float) or isinstance(jumplimit,int)):
        self.debugmsg('no jump filtering.  returning full range.')
        return (0,npts_curve-1)

    # find the step size between subsequent bias points
    # we make this relative to the lower point in the step
    # so that a big step is a big number
    steps=[]
    for idx in np.arange(1,npts_curve):
        stepsize=I[idx]-I[idx-1]
        if stepsize > self.zero:
            rel_stepsize = abs(stepsize/I[idx-1])
        elif stepsize < -self.zero:
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

def single_polynomial_fit_parameters(self,fit):
    '''
    determine the TES characteristics from the fit of single polynomial fit
    (see also the combined function fit)
    this is called from fit_iv()
    '''
    TES=fit['TES']
    TES_index=self.TES_index(TES)
    I=self.ADU2I(self.adu[TES_index,:])
    npts=len(I)

    
    # the coefficients of the polynomial fit
    a3=fit['fitinfo'][0][0]
    a2=fit['fitinfo'][0][1]
    a1=fit['fitinfo'][0][2]
    a0=fit['fitinfo'][0][3]

    # find turning where polynomial tangent is zero (i.e. first derivative is zero)
    t1=-a2/(3*a3)
    discriminant=a2**2 - 3*a1*a3
    if discriminant<0.0:
        fit['turning']=[None,None]
        fit['concavity']=[None,None]
        fit['turnover']=None
        fit['Iturnover']=None
        fit['inflection']=None
        # the following two can be set to something more appropriate
        fit['offset']=0.0
        fit['R1']=None
        return fit

    t2=math.sqrt(discriminant)/(3*a3)
    x0_0=t1+t2
    x0_1=t1-t2
    fit['turning']=[x0_0,x0_1]

    # check the concavity of the turning: up or down (+ve is up)
    fit['concavity']=[2*a2 + 6*a3*x0_0, 2*a2 + 6*a3*x0_1]

    # check if we have a valid turnover point within the range
    found_turnover=False
    idx=0
    for V0 in fit['turning']:
        concavity=fit['concavity'][idx]
        if (not V0==None):
            if concavity>0:
                found_turnover=True
                fit['turnover']=V0
        idx+=1
        
    if not found_turnover:
        fit['turnover']=None
        fit['Iturnover']=None

    n_turnings_within_range=0
    for V0 in fit['turning']:
        if (not V0==None) and V0>self.min_bias and V0<self.max_bias:
            n_turnings_within_range+=1     
    fit['turnings within range']=n_turnings_within_range

    # find the inflection point between the turning points
    inflection_V=-a2/(3*a3)
    fit['inflection']=inflection_V

    # if the inflection is between the turnover and the max bias,
    # then we fit a straight line to the final points
    # instead of using the fit all the way through
    if (not fit['turnover']==None) \
       and (inflection_V>fit['turnover']) \
       and (inflection_V<self.max_bias):
        # find the corresponding points to fit
        istart=fit['curve index']*fit['npts_curve']
        iend=istart+fit['npts_curve']
        xpts=self.bias_factor*self.vbias[istart:iend]
        gotit=False
        dv=xpts[1]-xpts[0]
        idx=0
        while not gotit and idx<fit['npts_curve']:
            if (dv>0.0 and xpts[idx]>=inflection_V)\
               or (dv<0.0 and xpts[idx]<=inflection_V): 
                gotit=True
            idx+=1

        idx-=1
        if (dv>0.0):
            ibeg=istart+idx
            istop=iend
        else:
            ibeg=istart
            istop=istart+idx+1

        xpts=self.bias_factor*self.vbias[ibeg:istop]
        ypts=I[ibeg:istop]
        fit['linefit xpts']=xpts
        fit['linefit ypts']=ypts
        self.debugmsg('single_polynomial_fit_parameters(%i): ibeg=%i, istop=%i' % (TES,ibeg,istop))
        linefit=np.polyfit(xpts,ypts,1,full=True)
        slope=linefit[0][0]
        b=linefit[0][1]
        if abs(slope)>self.zero:
            R1=1/slope
        else:
            R1=1/self.zero
        # offset forces the line to have I(max_bias)=max_bias (i.e. R=1 Ohm)
        Imax=slope*self.max_bias + b
        offset=self.max_bias-Imax
        fit['R1']=R1
        fit['offset']=offset
        if found_turnover:
            V0=fit['turnover']
            fit['Iturnover']=a0 + a1*V0 + a2*V0**2 + a3*V0**3 + offset

        return fit
        

        
    # if the above didn't work, we use the original curve fit 
    # we shift the fit curve up/down to have I(max_bias)=max_bias
    # which puts the max bias position at a point on the R=1 Ohm line
    V=self.max_bias
    Imax=a0 + a1*V + a2*(V**2) + a3*(V**3)
    offset=V-Imax
    fit['offset']=offset
    if found_turnover:
        V0=fit['turnover']
        fit['Iturnover']=a0 + a1*V0 + a2*V0**2 + a3*V0**3 + offset
    
    # find the tangent line of the fit to the I-V curve at the maximum bias
    # this should be equivalent to a circuit with resistance 1 Ohm
    # tangent is the first derivative of the polyfit
    slope=a1 + 2*a2*V + 3*a3*(V**2)
        
    # The line should have a slope equal to a circuit with resistance 1 Ohm
    if abs(slope)>self.zero:
        R1 = 1/slope
    else:
        R1=1/self.zero
    fit['R1']=R1
    return fit

def combined_fit_parameters(self,fit):
    '''
    determine the TES characteristics from the fit of multiple polynomials
    this is called from fit_iv()
    '''
    TES=fit['TES']
    TES_index=self.TES_index(TES)
    I=self.ADU2I(self.adu[TES_index,:])
    npts=len(I)

    # these are for compatibility with 3rd degree polynomial fit
    fit['turning']=[None,None]
    fit['concavity']=[None,None]
    fit['inflection']=None

    return fit


def do_polyfit(self,bias,curve):
    '''
    fit I-V curve to polynomial degree 3
    normalize the residual to the number of points in the fit
    '''
    self.debugmsg('I-V polyfit.  Single polynomial for the whole I-V curve.')
    npts=len(bias)
    polyfit=np.polyfit(bias,curve,3,full=True)
    residual=polyfit[1][0]/npts
    ret={}
    ret['fitinfo']=polyfit
    ret['residual']=residual
    return ret

def do_combinedfit(self,bias,curve):
    '''
    fit I-V curve to a combined polynomial 
    (see iv_function() below)
    '''
    self.debugmsg('I-V combined fit.  Multiple polynomials.')

    # initial guess
    turnover_idx=np.argmin(curve)
    Vturnover=bias[turnover_idx]
    Vmax=max(bias)
    Vmin=min(bias)
    Vnormal=Vturnover + 0.5*(Vmax-Vturnover)
    a0=1.0
    a1=1.0
    a2=1.0
    b0=1.0
    b1=1.0
    b2=1.0
    c0=1.0
    c1=5.0
    p0=[Vturnover,Vnormal,a0,a1,a2,b0,b1,b2,c0,c1]

    popt,pcov=curve_fit(self.iv_function,bias,curve,p0=p0)
    fitinfo=[popt,pcov]

    # calculate a performance measure
    npts=len(bias)
    Vturnover,Vnormal,a0,a1,a2,b0,b1,b2,c0,c1=popt
    Vfit=self.iv_function(bias,Vturnover,Vnormal,a0,a1,a2,b0,b1,b2,c0,c1)
    sigma2=(curve-Vfit)**2
    residual = np.sqrt( np.sum(sigma2) )/npts
    ret={}
    ret['fitinfo']=fitinfo
    ret['residual']=residual
    ret['turnover']=Vturnover
    ret['R1']=1.0/c1

    # find offset that puts current equal to max bias voltage (R=1 at Vbias=maximum)
    max_bias_idx=np.argmax(bias)
    max_bias=bias[max_bias_idx]
    Imax=curve[max_bias_idx]
    offset=max_bias-Imax
    ret['offset']=offset
    
    ret['Iturnover']=self.iv_function([Vturnover],Vturnover,Vnormal,a0,a1,a2,b0,b1,b2,c0,c1) + offset

    return ret

def iv_function(self,Vpts,Vturnover,Vnormal,a0,a1,a2,b0,b1,b2,c0,c1):
    '''
    function to fit I-V curve in three parts
      1. polynomial 2nd order below turnover bias
      2. polynomial 2nd order above turnover bias
      3. straight line in normal region

    there are 10 parameters to fit!
    '''    
    I=np.empty( (len(Vpts)) )
    for idx,V in enumerate(Vpts):
        if V<Vturnover:
            I[idx]=a0 + a1*V + a2*V*V
        elif V<Vnormal:
            I[idx]=b0 + b1*V + b2*V*V
        else:
            I[idx]=c0 + c1*V
    return I



def fit_iv(self,TES,jumplimit=None,curve_index=None,fitfunction='POLYNOMIAL'):
    '''
    fit the I-V curve to a polynomial

    if we're cycling, we always go down-up-down or up-down-up for a single cycle
    so a single IV curve is 1/(2*ncycles)

    we work directly with the uncalibrated data.
    The fit will be used to make the final adjustments

    optional arguments: 
       jumplimit:    this is the smallest step considered to be a jump in the data
       curve_index:  force the fit to use a particular curve in the cycle, and not simply the "best" one
       fitfunction:  use a 3rd degree polynomial, or a combination of polynomials
    '''
    if not isinstance(self.adu,np.ndarray):
        print('ERROR! No data!')
        return None
    
    TES_index=self.TES_index(TES)
    
    # return is a dictionary with various info
    fit={}
    fit['TES']=TES
    fit['fitfunction']=fitfunction.upper()

    I=self.ADU2I(self.adu[TES_index,:])
    npts=len(I)

    if self.cycle_vbias:
        ncurves=self.nbiascycles*2
    else:
        ncurves=self.nbiascycles
    npts_curve=int(npts/ncurves)
    fit['ncurves']=ncurves
    fit['npts_curve']=npts_curve
    self.debugmsg('number of curves: %i' % ncurves)
    self.debugmsg('npts per curve: %i' % npts_curve)
    
    # fit for each measured curve and find the best one
    best_residual=1./self.zero
    best_curve_index=0
    allfits=[]
    fitranges=[]
    istart=0
    for idx in range(ncurves):
        iend=istart+npts_curve
        ypts=I[istart:iend]
        self.debugmsg('cycle %i: fitting curve istart=%i, iend=%i' % ((idx+1),istart,iend))
        xpts=self.bias_factor*self.vbias[istart:iend] # should maybe use Vtes here? but there's a chance of recursion with Voffset.

        # filter out the big jumps
        # the return is the range of indexes of the acceptable points
        good_start,good_end=self.filter_jumps(ypts,jumplimit)
        npts_span=good_end-good_start
        if npts_span<11:
            self.debugmsg('couldn\'t find a large span without jumps! Fitting the whole curve...')
            good_start=0
            good_end=len(xpts)
            npts_span=npts_curve
        curve=ypts[good_start:good_end]
        bias=xpts[good_start:good_end]

        if fitfunction=='POLYNOMIAL':
            ivfit=self.do_polyfit(bias,curve)
        else:
            ivfit=self.do_combinedfit(bias,curve)

        for key in ivfit.keys(): fit[key]=ivfit[key] # it's a hack.    
        residual=ivfit['residual']
        allfits.append(ivfit['fitinfo'])
        fitranges.append((good_start,good_end))
        if abs(residual)<best_residual:
            best_residual=abs(residual)
            best_curve_index=idx
        istart+=npts_curve

    # from now on we use the best curve fit
    # unless there is request to override with the curve_index option
    fit['best curve index']=best_curve_index
    if not curve_index==None:
        if not isinstance(curve_index,int) or curve_index>=ncurves or curve_index<0:
            print('Invalid option for curve index:  Please give an integer between 0 and %i' % (ncurves-1))
            print('Using default:  best curve index=%i' % best_curve_index)
            curve_index=best_curve_index
    else:
        curve_index=best_curve_index
    fit['curve index']=curve_index
    fitinfo=allfits[curve_index]
    fit['fitinfo']=fitinfo
    fit['fit range']=fitranges[curve_index]

    if fitfunction=='POLYNOMIAL':
        fit=self.single_polynomial_fit_parameters(fit)
    else:
        fit=self.combined_fit_parameters(fit)

    keys=''
    for key in fit.keys():keys+=key+', '
    self.debugmsg('returning from fit_iv() with keys: %s' % keys)
    return fit


def draw_iv(self,I,colour='blue',axis=plt,label=None):
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
        axis.plot(self.bias_factor*self.vbias[0:npts],I,color=colour)
        axis.plot(self.bias_factor*self.vbias[npts-1],I[npts-1],color='red',marker='D',linestyle='none')

        tempstr='T$_\mathrm{bath}$=%0.2f mK' % (1000*self.temperature)
        axis.text(0.05,0.95,tempstr,va='top',ha='left',fontsize=14,transform=axis.transAxes)
        
        plt.pause(0.01)
        return
    
    if self.cycle_vbias:
        # plot down and up voltage with different linestyles
        mid=int(len(self.bias_factor*self.vbias)/2)
        axis.plot(self.bias_factor*self.vbias[0:mid],I[0:mid],linestyle='solid', color=colour)
        axis.plot(self.bias_factor*self.vbias[mid:-1], I[mid:-1], linestyle='dashed',color=colour)
        return
    
    axis.plot(self.bias_factor*self.vbias,I,color=colour)
    return

def setup_plot_iv(self,TES,xwin=True):
    if isinstance(self.obsdate,dt.datetime):
        ttl=str('QUBIC I-V curve for TES#%3i (%s)' % (TES,self.obsdate.strftime('%Y-%b-%d %H:%M UTC')))
    else:
        ttl=str('QUBIC I-V curve for TES#%3i with Vbias ranging from %.2fV to %.2fV' % (TES,self.min_bias,self.max_bias))
    if self.temperature==None:
        tempstr='unknown'
    else:
        tempstr=str('%.0f mK' % (1000*self.temperature))
    subttl=str('Array %s, ASIC #%i, Pixel #%i, Temperature %s' % (self.detector_name,self.asic,self.tes2pix(TES),tempstr))
    if xwin: plt.ion()
    else: plt.ioff()
    fig=plt.figure(figsize=self.figsize)
    fig.canvas.set_window_title('plt: '+ttl) 
    fig.suptitle(ttl+'\n'+subttl,fontsize=16)
    ax=plt.gca()
    ax.set_xlabel('Bias Voltage  /  V')
    ax.set_ylabel('Current  /  $\mu$A')
    ax.set_xlim([self.bias_factor*self.min_bias,self.bias_factor*self.max_bias])
    return fig,ax

def adjusted_iv(self,TES):
    '''
    return the adjusted I-V curve
    '''
    offset=self.offset(TES)
    Iadjusted=self.ADU2I(self.adu[self.TES_index(TES),:],offset=offset)
    return Iadjusted

def oplot_iv(self,TES,label=None):

    Iadjusted=self.adjusted_iv(TES)
    self.draw_iv(Iadjusted,label=label)
    
    return

def plot_iv(self,TES=None,fudge=1.0,multi=False,xwin=True):
    filterinfo=self.filterinfo(TES)
    if filterinfo==None:return None
    
    if multi:return self.plot_iv_multi()
    if TES==None:return self.plot_iv_physical_layout()
    if not isinstance(TES,int): return self.plot_iv_physical_layout()

    TES_index=self.TES_index(TES)
    fit=filterinfo['fit']
    
    if not isinstance(self.vbias,np.ndarray):
        print('ERROR: No Vbias.')
        return None
    
    fig,ax=self.setup_plot_iv(TES,xwin)

    # identify which fit function was used
    if 'fitfunction' not in fit.keys():
        fit['fitfunction']='POLYNOMIAL'
    txt='fit function = %s' % fit['fitfunction']
    
    # normalize the Current so that R=1 Ohm at the highest Voffset
    offset=self.offset(TES)
    txt+=str('\noffset=%.4e' % offset)
    Iadjusted=self.adjusted_iv(TES)
    self.oplot_iv(TES)
        
    # draw a line tangent to the fit at the highest Vbias
    # I0 here is the current extrapolated to Vbias=0
    R1,I0=self.draw_tangent(TES)
    
    R1=self.R1(TES)
    if not R1==None: txt+=str('\ndynamic normal resistance:  R$_1$=%.4f $\Omega$' % R1)

    # draw a fit to the I-V curve
    txt+=str('\nfit residual: %.4e' % filterinfo['residual'])
    bias,f=self.fitted_iv_curve(TES)
    plt.plot(bias,f,linestyle='dashed',color='red')

    # draw vertical lines to show the range used for the fit
    if 'fit range' in fit.keys():
        fit_istart,fit_iend=fit['fit range']
        fit_vstart=self.bias_factor*self.vbias[fit_istart]
        fit_vend=self.bias_factor*self.vbias[fit_iend-1]
        plt.plot([fit_vstart,fit_vstart],[min(Iadjusted),max(Iadjusted)],color='red',linestyle='dashed')
        plt.plot([fit_vend,fit_vend],[min(Iadjusted),max(Iadjusted)],color='red',linestyle='dashed')
    

    # note the turnover point
    if fit['turnover']==None:
        txt+='\nNo turnover!'
    else:
        v0=fit['turnover']
        xpts=[v0,v0]
        ypts=[min(Iadjusted),max(Iadjusted)]
        plt.plot(xpts,ypts,linestyle='dashed',color='green')
        txt+=str('\nturnover Vbias=%.2fV' % v0)
        # Iturnover is the current at Vturnover
        if 'Iturnover' in fit.keys():
            Iturnover=fit['Iturnover']
        else:
            Iturnover=min(Iadjusted)
        txt+=str('\nI$_\mathrm{turnover}$=%.2f $\mu$A' % Iturnover)
        

    # add room temp results, if loaded
    if not self.transdic==None:
        PIX=self.tes2pix(TES)
        # self.debugmsg('table lookup for PIX=%i' % PIX)
        entry=self.lookup_TEStable(key='PIX',value=PIX)
        R300=entry['R300']
        if isinstance(R300,float):
            R300str='%.2f $\Omega$' % R300
        else:
            R300str=R300
        txt+='\nRoom Temperature Resistance: %s' % R300str
        openloop=entry['OpenLoop']
        txt+='\nOpen Loop Test:  %s' % openloop
    
    is_good=self.is_good_iv(TES)
    comment=filterinfo['comment']
    if not is_good:txt+=str('\nFlagged as BAD:  %s' % comment)

    # write out the comments
    text_x=self.bias_factor*(self.min_bias + 0.95*(self.max_bias-self.min_bias))
    text_y=min(Iadjusted) + 0.98*(max(Iadjusted)-min(Iadjusted))
    plt.text(text_x,text_y,txt,va='top',ha='right',fontsize=12)
    pngname=str('TES%03i_IV_array-%s_ASIC%i_%s.png' % (TES,self.detector_name,self.asic,self.obsdate.strftime('%Y%m%dT%H%M%SUTC')))
    pngname_fullpath=self.output_filename(pngname)
    if isinstance(pngname_fullpath,str): plt.savefig(pngname_fullpath,format='png',dpi=100,bbox_inches='tight')
    if xwin: plt.show()
    else: plt.close('all')
    return fig

def plot_pv(self,TES,xwin=True):
    ttl=str('QUBIC P-V curve for TES#%3i (%s)' % (TES,self.obsdate.strftime('%Y-%b-%d %H:%M UTC')))
    if self.temperature==None:
        tempstr='unknown'
    else:
        tempstr=str('%.0f mK' % (1000*self.temperature))
    subttl=str('Array %s, ASIC #%i, Pixel #%i, Temperature %s' % (self.detector_name,self.asic,self.tes2pix(TES),tempstr))
    if xwin: plt.ion()
    else: plt.ioff()
    fig,ax=plt.subplots(1,1,figsize=self.figsize)
    fig.canvas.set_window_title('plt: '+ttl) 
    fig.suptitle(ttl+'\n'+subttl,fontsize=16)
    ax.set_xlabel('Bias Voltage  /  V')
    ax.set_ylabel('P$_\mathrm{TES}$  /  $p$A')
    ax.set_xlim([self.min_bias,self.max_bias])

    istart,iend=self.selected_iv_curve(TES)
    Ptes=self.Ptes(TES)[istart:iend]
    bias=self.bias_factor*self.vbias[istart:iend]
    plt.plot(bias,Ptes)
    
    pngname=str('TES%03i_PV_array-%s_ASIC%i_%s.png' % (TES,self.detector_name,self.asic,self.obsdate.strftime('%Y%m%dT%H%M%SUTC')))
    pngname_fullpath=self.output_filename(pngname)
    if isinstance(pngname_fullpath,str): plt.savefig(pngname_fullpath,format='png',dpi=100,bbox_inches='tight')
    if xwin: plt.show()
    else: plt.close('all')
    return fig,ax
    
def plot_rp(self,TES,xwin=True):
    if self.R1(TES)==None:
        print('No normal resistance estimate.')
        return None

    istart,iend=self.selected_iv_curve(TES)
    
    Rn_ratio=self.Rn_ratio(TES)[istart:iend]
    Ptes=self.Ptes(TES)[istart:iend]
    Pbias=self.Pbias(TES)
    lbl='P$_\mathrm{bias}=$%.2f pW' % Pbias

    Rmin=min(Rn_ratio)
    Rmax=max(Rn_ratio)
    Rspan=Rmax-Rmin
    plot_Rmin=Rmin-0.2*Rspan
    plot_Rmax=100.
    
    Pmin=min(Ptes)
    Pmax=max(Ptes)
    Pspan=Pmax-Pmin
    plot_Pmin=Pmin-0.05*Pspan
    plot_Pmax=Pmax+0.2*Pspan
    
    ttl=str('QUBIC R-P curve for TES#%3i (%s)' % (TES,self.obsdate.strftime('%Y-%b-%d %H:%M UTC')))
    if self.temperature==None:
        tempstr='unknown'
    else:
        tempstr=str('%.0f mK' % (1000*self.temperature))
    subttl=str('Array %s, ASIC #%i, Pixel #%i, Temperature %s' % (self.detector_name,self.asic,self.tes2pix(TES),tempstr))
    if xwin: plt.ion()
    else: plt.ioff()
    fig,ax=plt.subplots(1,1,figsize=self.figsize)
    fig.canvas.set_window_title('plt: '+ttl) 
    fig.suptitle(ttl+'\n'+subttl,fontsize=16)
    ax.set_xlabel('P$_\mathrm{TES}$  /  pW')
    ax.set_ylabel('$\\frac{R_\mathrm{TES}}{R_\mathrm{normal}}$ / %')

    plt.plot(Ptes,Rn_ratio)
    plt.plot([Pbias,Pbias],[0,90],linestyle='dashed',color='green')
    plt.plot([plot_Pmin,Pbias],[90,90],linestyle='dashed',color='green')
    ax.set_xlim([plot_Pmin,plot_Pmax])
    ax.set_ylim([plot_Rmin,plot_Rmax])

    text_x=plot_Pmax-0.3*Pspan
    text_y=plot_Rmin+0.5*Rspan
    plt.text(text_x,text_y,lbl)
    
    pngname=str('TES%03i_RP_array-%s_ASIC%i_%s.png' % (TES,self.detector_name,self.asic,self.obsdate.strftime('%Y%m%dT%H%M%SUTC')))
    pngname_fullpath=self.output_filename(pngname)
    if isinstance(pngname_fullpath,str): plt.savefig(pngname_fullpath,format='png',dpi=100,bbox_inches='tight')
    if xwin: plt.show()
    else: plt.close('all')
    return fig,ax


                
def make_Vbias(self,cycle=True,ncycles=2,vmin=0.5,vmax=3.0,dv=0.002,lowhigh=True):
    '''
    the bias voltage values used during the I-V curve measurement
    '''

    if vmax<0.0:
        vmax=np.abs(vmax)
        print('No negative values for bias! Setting max bias to %.2f V' % vmax)

    if vmax>self.max_permitted_bias:
        print('It is dangerous to set the bias voltage greater than %.2f V.' % self.max_permitted_bias)
        print('Setting maximum bias to %.2f V' % self.max_permitted_bias)
        vmax=self.max_permitted_bias

    if vmin<0.0:
        print('No negative values! Setting minimum bias to 0 V')
        vmin=0.0

    if ncycles<1:
        print('You need at least one cycle! Setting ncycles=1')
        ncycles=1
    
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

    vbias=onecycle
    for n in range(ncycles-1):
        vbias=np.concatenate((vbias,onecycle),0)
    
    self.vbias=vbias
    self.min_bias=min(self.vbias)
    self.max_bias=max(self.vbias)
    self.max_bias_position=np.argmax(self.vbias)
    return vbias


def filter_iv(self,TES,
              residual_limit=3.0,
              abs_amplitude_limit=0.01,
              rel_amplitude_limit=0.1,
              bias_margin=0.2,
              jumplimit=None,
              curve_index=None,
              fitfunction='POLYNOMIAL'):
    '''
    determine if this is a good TES from the I-V curve
    '''
    TES_index=self.TES_index(TES)
    
    # dictionary to return stuff
    ret={}
    ret['TES']=TES
    ret['is_good']=True
    ret['comment']='no comment'

    # fit to a polynomial. The fit will be for the best measured curve if it's cycled bias
    fit=self.fit_iv(TES,jumplimit,curve_index,fitfunction)
    ret['fit']=fit
    residual=fit['residual']
    ret['residual']=residual
    offset=fit['offset']
    ret['offset']=offset
    ADU=self.adu[TES_index,:]
    Iadjusted=self.ADU2I(ADU,offset=offset,fudge=1.0)
    ret['turnover']=fit['turnover']

    # first filter:  is it a good fit?
    if residual>residual_limit:
        ret['is_good']=False
        ret['comment']='bad poly fit'
        return self.assign_filterinfo(TES,ret)
    
    # second filter: small amplitude is rejected
    # we use the best curve as determined by the fit unless curve_index was specified
    curve_index=fit['curve index']
    npts=fit['npts_curve']
    istart=npts*curve_index
    iend=npts*(curve_index+1)
    meanval=Iadjusted[istart:iend].mean()
    maxval=max(Iadjusted[istart:iend])
    minval=min(Iadjusted[istart:iend])
    spread=abs(maxval-minval)
    self.debugmsg('maxval=%f, minval=%f, abs amplitude=%f' % (maxval,minval,spread))
    ret['abs_amplitude']=spread
    if spread<abs_amplitude_limit:
        ret['is_good']=False
        ret['comment']='current too low'
        return self.assign_filterinfo(TES,ret)
        
    # third filter: peak to peak amplitude
    rel_amplitude=abs(spread/meanval)
    ret['rel_amplitude']=rel_amplitude
    if rel_amplitude<rel_amplitude_limit:
        ret['is_good']=False
        ret['comment']='current peak-to-peak too small'
        return self.assign_filterinfo(TES,ret)
    
    # fourth filter: do we find a valid turnover for the Vbias?
    ret['turnover']=fit['turnover']
    if fit['turning']==None or fit['turnover']==None:
        ret['is_good']=False
        ret['comment']='no turnover'
        return self.assign_filterinfo(TES,ret)

    # fifth filter: is the operational point (the turnover) within the acceptable range?
    if ret['turnover']<self.min_bias+bias_margin or ret['turnover']>self.max_bias-bias_margin:
        ret['is_good']=False
        ret['comment']='operation point outside acceptable range'
        return self.assign_filterinfo(TES,ret)

    # sixth filter:  do we have both turning points within the bias range?
    # maybe I should delete this filter
    #if fit['turnings within range']>1:
    #    ret['is_good']=False
    #    ret['comment']='bad I-V profile'
    #    return self.assign_filterinfo(TES,ret)
    
    
    # we only get this far if it's a good I-V
    return self.assign_filterinfo(TES,ret)

def filter_iv_all(self,
                  residual_limit=3.0,
                  abs_amplitude_limit=0.01,
                  rel_amplitude_limit=0.1,
                  bias_margin=0.2,
                  jumplimit=None,
                  fitfunction='POLYNOMIAL'):
    '''
    find which TES are good
    '''
    if not isinstance(self.adu,np.ndarray):
        print('No data!  Please read a file, or run a measurement.')
        return None

    # return a list with the filter info for each TES
    filtersummary=[]

    # go through each filter.  Jump out and examine the next I-V curve as soon as a bad I-V is found
    for TES_index in range(self.NPIXELS):
        TES=TES_index+1
        self.debugmsg('running filter on TES %03i' % TES)
        filterinfo=self.filter_iv(TES,
                                  residual_limit,
                                  abs_amplitude_limit,
                                  rel_amplitude_limit,
                                  bias_margin,
                                  jumplimit,
                                  curve_index=None,
                                  fitfunction=fitfunction)
        filtersummary.append(filterinfo)
        
    self.filtersummary=filtersummary
    return filtersummary

def save_filter(self):
    '''
    save the filter to a picke file
    '''
    datefmt='%Y%m%dT%H%M%SUTC'
    datestr=self.obsdate.strftime(datefmt)
    picklename=str('QUBIC_TES_%s.filter.pickle' % datestr)
    h=open(picklename,'w')
    pickle.dump(self.filtersummary,h)
    h.close()
    return

def read_filter(self):
    '''
    read the filter from a pickle file
    '''
    datefmt='%Y%m%dT%H%M%SUTC'
    datestr=self.obsdate.strftime(datefmt)
    picklename=str('QUBIC_TES_%s.filter.pickle' % datestr)
    if not os.path.exists(picklename):
        print('No previously saved filter information: %s' % picklename)
        return None

    print('Reading previously saved filter information: %s' % picklename)
    h=open(picklename,'r')
    filtersummary=pickle.load(h)
    h.close()
    self.filtersummary=filtersummary
    return True

def read_ADU_file(self,filename):
    '''
    legacy:  a few files were produced in this format before the FITS file was defined
    '''
    if not os.path.exists(filename):
        print("file not found: ",filename)
        return None

    # try to get date from filename
    self.assign_obsdate(self.read_date_from_filename(filename))

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
        adu=np.array(X)
    self.assign_ADU(adu)
    return adu

def iv_tex_table_entry(self,TES):
    TES_index=self.TES_index(TES)
    PIX=self.tes2pix(TES)
    if self.turnover(TES)==None:
        turnover='-'
    else:
        turnover=str('%.2f V' % self.turnover(TES))

    R1=self.R1(TES)
    if R1==None or R1>10000:
        R1str='-'
    else:
        if abs(R1)<100:
            R1str=str('%.2f $\Omega$' % R1)
        else:
            R1str=str('%.2e $\Omega$' % R1)

    comment=self.filtersummary[TES_index]['comment']
    if comment=='no comment': comment='good'

    if self.transdic==None:
        R300str='--'
        openloop='--'
        cf='--'
    else:
        # self.debugmsg('table lookup for PIX=%i' % PIX)
        entry=self.lookup_TEStable(key='PIX',value=PIX)
        R300=entry['R300']
        if isinstance(R300,float):
            if abs(R300)<10000:
                R300str='%.1f $\Omega$' % R300
            else:
                R300str='%.2e $\Omega$' % R300
        else:
            R300str=R300

        openloop=entry['OpenLoop']
        cf=entry['CarbonFibre']

    comment_entry=str('\\comment{%s}' % comment)
    rowstr='%3i & %3i & %s & %s & %s & %s & %s & %s' % (TES, PIX, turnover, R1str, R300str, openloop, cf, comment_entry)
    return rowstr

def make_iv_tex_report(self,tableonly=False):
    '''
    make a report in LaTeX.  
    This relies on the data in self.filtersummary.  See self.filter_iv_all() above
    '''
    if not isinstance(self.adu,np.ndarray):
        print('ERROR! No data!')
        return None
    
    thumbnailplot=str('TES_IV_array-%s_ASIC%i_%s.png'     % (self.detector_name,self.asic,self.obsdate.strftime('%Y%m%dT%H%M%SUTC')))
    allplot      =str('TES_IV_array-%s_ASIC%i_all_%s.png' % (self.detector_name,self.asic,self.obsdate.strftime('%Y%m%dT%H%M%SUTC')))
    pattern      =str('TES???_IV_array-%s_ASIC%i_%s.png'  % (self.detector_name,self.asic,self.obsdate.strftime('%Y%m%dT%H%M%SUTC')))

    # do the globbing in working directory
    cwd=os.getcwd()
    subdir=self.data_subdir()
    if isinstance(subdir,str):
        workdir='%s/%s' % (self.datadir,subdir)
    else:
        workdir=self.datadir
    os.chdir(workdir) # move to data directory
    iv_plots=glob(pattern)
    os.chdir(cwd) # and return to previous directory

    iv_plots.sort()

    if len(iv_plots)<self.NPIXELS:
        print('WARNING: Did not find all the I-V plots!')

    observer=self.observer.replace('<','$<$').replace('>','$>$')
    
    texfilename=str('TES_IV_array-%s_ASIC%i_%s.tex' % (self.detector_name,self.asic,self.obsdate.strftime('%Y%m%dT%H%M%SUTC')))
    texfilename_fullpath=self.output_filename(texfilename)
    if not isinstance(texfilename_fullpath,str):
        print('ERROR! Not possible to write tex file.')
        return None
    
    h=open(texfilename_fullpath,'w')
    h.write('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n')
    h.write('%%%%% WARNING!  Automatically generated file.  Do not edit! %%%%%\n')
    h.write('%%%%% This file could be overwritten                        %%%%%\n')
    h.write(dt.datetime.utcnow().strftime('%%%%%%%%%% File generated %Y-%m-%d %H:%M:%S UTC                %%%%%%%%%%\n'))
    h.write('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n')
    h.write('\\documentclass[a4paper,12pt]{article}\n')
    h.write('\\usepackage{graphicx}\n')
    h.write('\\usepackage{hyperref}\n')
    h.write('\\usepackage{longtable}\n')
    h.write('\\usepackage{setspace}\n')
    h.write('\\newcommand{\\comment}[1]{\n\\begin{minipage}[t]{20ex}\n\\setstretch{0.5}\\flushleft\\noindent\n#1\n\\vspace*{1ex}\n\\end{minipage}}\n')
    h.write('\\newlength{\\openlooplen}\n')
    h.write('\\settowidth{\\openlooplen}{ooop}\n')
    h.write('\\newlength{\\cflen}\n')
    h.write('\\settowidth{\\cflen}{carbon}\n')
    h.write('\\newcommand{\\openloopheading}{\n\\begin{minipage}[t]{\\openlooplen}\nopen\\\\\nloop\n\\end{minipage}\n}\n')
    h.write('\\newcommand{\\cfheading}{\n\\begin{minipage}[t]{\\cflen}\ncarbon\\\\\nfibre\n\\end{minipage}\n}\n')
    
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
    h.write('\\item Array %s\n' % self.detector_name)
    h.write('\\item ASIC %i\n' % self.asic)
    if self.temperature==None:
        tempstr='unknown'
    else:
        tempstr=str('%.0f mK' % (1000*self.temperature))
    h.write('\\item TES physical temperature: %s\n' % tempstr)

    h.write('\\item %i pixels are flagged as bad.\n\\item %.1f\\%s of the array is good\n'\
            % ( self.NPIXELS-self.ngood(), 100.0*self.ngood()/self.NPIXELS, '%' ))
    h.write('\\end{itemize}\n')
    
    h.write('\n\\vspace*{3ex}\n\\noindent This document includes the following:\n')
    h.write('\\begin{itemize}\n')
    h.write('\\item Summary Table including turnover points and other parameters for each TES\n')
    h.write('\\item Plot of all the I-V curves, each in its corresponding location in the focal plane\n')
    h.write('\\item Plot of all the good I-V curves on a single plot\n')
    h.write('\\item Plot of each TES I-V curve (%i plots)\n' % self.NPIXELS)
    h.write('\\end{itemize}\n\\clearpage\n')

    ncols=1
    nrows=int(self.NPIXELS/ncols)
    colfmt='|r|r|r|r|r|l|l|l|'
    headline1='\\multicolumn{1}{|c|}{TES} & '\
               '\\multicolumn{1}{|c|}{pix} & '\
               '\\multicolumn{1}{c|}{V$_{\\rm turnover}$} & '\
               '\\multicolumn{1}{c|}{R$_1$} & '\
               '\\multicolumn{1}{c|}{R$_{\\rm 300K}$} & '\
               '\\multicolumn{1}{c|}{\\openloopheading} &'\
               '\\multicolumn{1}{c|}{\\cfheading} &'\
               '\\multicolumn{1}{c|}{comment}'
    headline=''
    headline+=headline1
    if ncols>1:
        for j in range(ncols-1):
            colfmt+='|||r|r|'
            headline+=' & '+headline1 
    h.write('\\noindent\\begin{longtable}{%s}\n' % colfmt)
    h.write('\\caption{Summary Table for TES\\\\\n')
    h.write('The carbon fibre measurements are from Sophie Henrot Versill\\a\'e, see \\url{http://qubic.in2p3.fr/wiki/pmwiki.php/TD/P73TestWithACarbonFiberSource}.\\\\\n')
    h.write('Results of the open loop test and the room temperature measurements are from Damien Pr\\^ele}\\\\\n')
    h.write('\\hline\n')
    h.write(headline+'\\\\ \n')
    h.write('\\hline\\endhead\n')
    h.write('\\hline\\endfoot\n')
    for i in range(nrows):
        for j in range(ncols):
            TES_index=i+j*nrows
            TES=TES_index+1
            rowstr=self.iv_tex_table_entry(TES)
            h.write(rowstr)
            if j<ncols-1: h.write(' &')
            else: h.write('\\\\\n')
    h.write('\\hline\n')
    h.write('\\end{longtable}\n\\clearpage\n')


    # make a table of disagreement
    if not self.transdic==None:
        h.write('\\noindent\\begin{longtable}{%s}\n' % colfmt)
        h.write('\\caption{Table of Disagreement\\\\\n')
        h.write('The carbon fibre measurements are from Sophie Henrot Versill\\a\'e, see \\url{http://qubic.in2p3.fr/wiki/pmwiki.php/TD/P73TestWithACarbonFiberSource}.\\\\\n')
        h.write('Results of the open loop test and the room temperature measurements are from Damien Pr\\^ele}\\\\\n')
        h.write('\\hline\n')
        h.write(headline+'\\\\ \n')
        h.write('\\hline\\endhead\n')
        h.write('\\hline\\endfoot\n')
        for TES_index in range(self.NPIXELS):
            TES=TES_index+1
            PIX=self.tes2pix(TES)
            entry=self.lookup_TEStable(key='PIX',value=PIX)

            if entry['CarbonFibre']=='good':
                is_good_CF=True
            else:
                is_good_CF=False

            if entry['OpenLoop']=='good':
                is_good_OL=True
            else:
                is_good_OL=False

            R300=entry['R300']
            is_good_R300=False
            if isinstance(entry['R300'],float):
                if abs(R300)<10000: is_good_R300=True
                
            '''
            if ((self.is_good_iv(TES) and (not is_good_CF
                                           or not is_good_OL
                                           or not is_good_R300))
                or (not self.is_good_iv(TES) and (is_good_CF
                                                  or is_good_OL
                                                  or is_good_R300))):
            '''
            if ((self.is_good_iv(TES) and not is_good_CF)\
                or (not self.is_good_iv(TES) and is_good_CF)):
                
                rowstr=self.iv_tex_table_entry(TES)
                h.write(rowstr)
                h.write('\\\\\n')
                
        h.write('\\hline\n')
        h.write('\\end{longtable}\n\\clearpage\n')
    

    if tableonly:
        h.write('\n\n\\end{document}\n')
        h.close()
        return texfilename_fullpath
        
    
    h.write('\n\\noindent\\includegraphics[width=0.8\\linewidth,clip]{%s}\\\\' % thumbnailplot)
    h.write('\n\\includegraphics[width=0.8\\linewidth,clip]{%s}\n\\clearpage\n\\noindent' % allplot)
    for png in iv_plots:
        h.write('\n\\includegraphics[width=0.8\\linewidth,clip]{%s}\\\\' % png)

    
    
    h.write('\n\n\\end{document}\n')
    h.close()
    return texfilename_fullpath


def make_iv_report(self):
    '''
    do all the business to generate the I-V report document
    '''
    if not isinstance(self.adu,np.ndarray):
        print('ERROR! No data!')
        return None

    # plot all the I-V in the focal-plane map
    self.figsize=(14,14)
    self.plot_iv_physical_layout(xwin=False)

    # plot all the good I-V curves on a single plot
    self.plot_iv_all(selection=self.is_good_iv(),xwin=False)

    # plot each I-V curve
    self.figsize=(16,12)
    for TES_index in range(self.NPIXELS):
        self.plot_iv(TES_index+1,xwin=False)

    # generate the LaTeX file
    texname=self.make_iv_tex_report()
    if not isinstance(texname,str):return None

    # process the LaTeX file a couple of times
    cwd=os.getcwd()
    subdir=self.data_subdir()
    if isinstance(subdir,str):
        workdir='%s/%s' % (self.datadir,subdir)
    else:
        workdir=self.datadir
    os.chdir(workdir) # move to data directory
    cmd='pdflatex %s' % texname
    os.system(cmd)
    os.system(cmd)
    os.chdir(cwd) # and return to previous directory
    pdfname=texname.replace('.tex','.pdf')
    return

def iv2txt(self,TES):
    '''
    extract the I-V data from a given TES to a text file with two columns
    '''
    if not isinstance(self.adu,np.ndarray):
        print('ERROR! No Data.')
        return None
    
    fname='QUBIC_TES%03i_array-%s_ASIC%i_IV_%s.txt' % (TES,self.detector_name,self.asic,self.obsdate.strftime('%Y%m%dT%H%M%S'))
    h=open(fname,'w')
    Ites=self.Ites(TES)
    if not isinstance(Ites,np.ndarray):return None
    
    Vtes=self.Vtes(TES)
    for idx in range(len(Ites)):
        h.write('%.6e %.6e\n' % (Vtes[idx],Ites[idx]))
    h.close()
    return fname


###################################################
### helper functions to return info from the filter
###################################################

def filterinfo(self,TES=None):
    '''
    return the filterinfo for a given TES
    '''
    if not isinstance(self.adu,np.ndarray):
        print('ERROR! No data!')
        return None

    # if no TES is specified, return the whole list
    if TES==None:
        # if filter has not been run, run it with defaults
        for TES_index in range(self.NPIXELS):
            f=self.filtersummary[TES_index]
            if f==None: f=self.filter_iv(TES_index+1)
            return self.filtersummary

    # if not a valid TES, return None
    if not isinstance(TES,int) or TES<1 or TES>self.NPIXELS:
        print('please enter a valid TES number between 1 and %i.' % self.NPIXELS)
        return None

    # if filter has not been run, run it with defaults
    f=self.filtersummary[self.TES_index(TES)]
    if f==None: f=self.filter_iv(TES)
    return self.filtersummary[self.TES_index(TES)]

def assign_filterinfo(self,TES,filterinfo):
    '''
    assign the dictionary of filter info to the filtersummary list
    '''
    self.filtersummary[self.TES_index(TES)]=filterinfo
    return filterinfo
    
def is_good_iv(self,TES=None):
    '''
    return the judgement about a TES
    if TES==None, return a list of all TES determinations
    '''

    filterinfo=self.filterinfo(TES)
    if filterinfo==None:return False

    if TES==None:
        filtersummary=filterinfo
        is_good=[]
        for finfo in filtersummary:
            is_good.append(finfo['is_good'])
        return is_good
    return filterinfo['is_good']

def good_index(self):
    '''
    return a list of indexes corresponding to the good TES
    '''
    good_index=[]
    for TES_index in range(self.NPIXELS):
        TES=TES_index+1
        if self.is_good_iv(TES):good_index.append(TES_index)
    return good_index
    
def ngood(self):
    '''
    return the number of good TES
    '''    
    ngood=0
    for TES_index in range(self.NPIXELS):
        TES=TES_index+1
        if self.is_good_iv(TES):ngood+=1
    return ngood

def turnover(self,TES=None):
    '''
    return the turnover (operation) voltage for the TES
    if TES==None, return a list for all the TES
    '''
    filterinfo=self.filterinfo(TES)
    if filterinfo==None:return None
        
    if TES==None:
        filtersummary=filterinfo
        turnover=[]
        for finfo in filtersummary:
            turnover.append(finfo['fit']['turnover'])
        return turnover
    return filterinfo['fit']['turnover']

def offset(self,TES=None):
    '''
    return the offset current for the TES
    if TES==None, return a list for all the TES
    '''
    filterinfo=self.filterinfo(TES)
    if filterinfo==None:return 0.0
        
    if TES==None:
        filtersummary=filterinfo
        turnover=[]
        for finfo in filtersummary:
            turnover.append(finfo['fit']['offset'])
        return turnover
    return filterinfo['fit']['offset']

def R1(self,TES=None):
    '''
    return the dynamic normal resistance for the TES
    if TES==None, return a list for all the TES
    '''
    filterinfo=self.filterinfo(TES)
    if filterinfo==None:return None
    if TES==None:
        filtersummary=filterinfo
        turnover=[]
        for finfo in filtersummary:
            turnover.append(finfo['fit']['R1'])
        return turnover
    return filterinfo['fit']['R1']

def Rn(self,TES=None):
    '''
    this is an alias for R1
    '''
    return self.R1(TES)

def selected_iv_curve(self,TES):
    '''
    return the index end points which selects the I-V cycle of the measurement used in the fit
    '''
    filterinfo=self.filterinfo(TES)
    if filterinfo==None:return None
    
    if 'curve index' in filterinfo['fit'].keys():
        curve_index=filterinfo['fit']['curve index']
    else:
        curve_index=filterinfo['fit']['best curve index']

    npts_curve=filterinfo['fit']['npts_curve']
    istart=curve_index*npts_curve
    iend=istart+npts_curve
    return (istart,iend)


def Ites(self,TES):
    '''
    return the TES current in Amps (not in microAmps)
    '''
    filterinfo=self.filterinfo(TES)
    if filterinfo==None:return None
    
    Ites=self.adjusted_iv(TES)*1e-6 # Amps
    return Ites

def Vtes(self,TES):
    '''
    return the Vtes
    '''
    Ites=self.Ites(TES)
    if not isinstance(Ites,np.ndarray):return None
    
    Vtes=self.Rshunt*((self.vbias*self.bias_factor)/self.Rbias-Ites)
    return Vtes

def Ptes(self,TES):
    '''
    return the power on the TES as a function of bias
    '''
    filterinfo=self.filterinfo(TES)
    if filterinfo==None:return None
    
    Ptes=self.Ites(TES)*self.Vtes(TES)*1e12 # pW
    return Ptes


def Rn_ratio(self,TES):
    '''
    return the ratio of TES resistance to Normal resistance
    '''
    if self.R1(TES)==None:return None

    Rn=self.Vtes(TES)/self.Ites(TES)
    Rn_ratio=100*Rn/self.R1(TES) # percent

    return Rn_ratio

def Pbias(self,TES):
    '''
    find the Pbias at 90% Rn
    '''    
    filterinfo=self.filterinfo(TES)
    if filterinfo==None:return None

    Rn_ratio=self.Rn_ratio(TES)
    if not isinstance(Rn_ratio,np.ndarray):return None

    istart,iend=self.selected_iv_curve(TES)

    Rn_ratio=Rn_ratio[istart:iend]
    Ptes=self.Ptes(TES)
    Ptes=Ptes[istart:iend]
    
    # check that Rn_ratio is increasing
    increasing=np.diff(Rn_ratio).mean()
    if increasing<0:
        Pbias=np.interp(90., np.flip(Rn_ratio,0), np.flip(Ptes,0))
    else:
        Pbias=np.interp(90., Rn_ratio, Ptes)

    return Pbias

