'''
$Id: plot_physical_layout.py
$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
$created: Tue 01 Aug 2017 16:53:52 CEST
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

plot a poster of the layout of the QUBIC TES array
'''
from __future__ import division, print_function
import numpy as np
from qubicpack import qubicpack as qp
import matplotlib.pyplot as plt

def mylut(v,vmin=3.0,vmax=9.0):
    vfractional=(v-vmin)/(vmax-vmin)
    colourmap = plt.cm.get_cmap('Spectral_r')
    rgb=colourmap(vfractional)
    return rgb

def plot_physical_layout(a1=None,a2=None,figsize=(16,16),xwin=True,lutmin=None,lutmax=None):
    '''
    plot an image of the TES array labeling each pixel
    plot the I-V curves in the appropriate boxes if a1 and/or a2 given
    '''

    obj_list=[a1,a2]
    asic1_obj=None
    asic2_obj=None
    temperature=None
    temperature_str=''
    detector_name='undefined'
    for obj in obj_list:
        if isinstance(obj,qp):
            temperature=obj.temperature
            detector_name=obj.detector_name
            if obj.asic==1:
                asic1_obj=obj
            elif obj.asic==2:
                asic2_obj=obj
            else:
                print('PROBLEM! QubicPack object does not have a valid ASIC definition')
                return None

        
    if asic1_obj is None:
        asic1_obj=qp()
        asic1_obj.assign_asic(1)
        asic1_fontsize=figsize[0]
    if asic2_obj is None:
        asic2_obj=qp()
        asic2_obj.assign_asic(2)
        asic2_fontsize=figsize[0]


    # Option:  a1 and a2 can be simply arrays with numbers to use as the colours for each pixel
    asic1_mapdata = False
    asic2_mapdata = False
    if (isinstance(a1,np.ndarray) or isinstance(a1,list)) and len(a1)==128:
        print('using mapping data for asic 1')
        asic1_mapdata = True
    if (isinstance(a2,np.ndarray) or isinstance(a2,list)) and len(a2)==128:
        print('using mapping data for asic 2')
        asic2_mapdata = True

    if lutmin is None:
        if asic1_mapdata and asic2_mapdata:
            lutmin = min( min(a1),min(a2) )
        elif asic1_mapdata:
            lutmin = min(a1)
        elif asic2_mapdata:
            lutmin = min(a2)
    if lutmax is None:
        if asic1_mapdata and asic2_mapdata:
            lutmax = max( max(a1),max(a2) )
        elif asic1_mapdata:
            lutmax = max(a1)
        elif asic2_mapdata:
            lutmax = max(a2)

    asic1_data=True
    asic1_fontsize=8
    asic2_data=True
    asic2_fontsize=8
    if not asic1_obj.exist_iv_data():
        asic1_data=False
        asic1_fontsize=figsize[0]
        asic1_subttl='ASIC 1 blue background'
    else:
        asic1_subttl='Array %s ASIC1 black curves' % asic1_obj.detector_name
    if not asic2_obj.exist_iv_data():
        asic2_data=False
        asic2_fontsize=figsize[0]
        asic2_subttl='ASIC 2 green background'
    else:
        asic2_subttl='Array %s ASIC2 blue curves' % asic2_obj.detector_name

    asic1_obj.figsize=figsize
    fontsize=figsize[0]
    ttlfontsize=figsize[0]*1.2

    nrows=asic1_obj.pix_grid.shape[0]
    ncols=asic1_obj.pix_grid.shape[1]

    if temperature is not None: temperature_str='%.0fmK' % (1000*temperature)

    if xwin: plt.ion()
    else: plt.ioff()
    fig,ax=plt.subplots(nrows,ncols,figsize=asic1_obj.figsize)
    fig.text(0.5,0.985,'QUBIC TES array',ha='center',fontsize=ttlfontsize)
    pngname='TES_Array-%s_%s.png' % (detector_name,temperature_str)
    if xwin: fig.canvas.set_window_title('plt:  QUBIC TES array')

    ngood=0
    npix=0
    if asic1_data:
        asic1_subttl+=', data from %s, T$_\mathrm{bath}$=%.3fmK'\
                       % (asic1_obj.obsdate.strftime('%Y-%m-%d %H:%M'),asic1_obj.temperature*1000)
        ngood+=asic1_obj.ngood()
        npix+=asic1_obj.NPIXELS
    if asic2_data:
        asic2_subttl+=', data from %s, T$_\mathrm{bath}$=%.3fmK'\
                       % (asic2_obj.obsdate.strftime('%Y-%m-%d %H:%M'),asic2_obj.temperature*1000)
        ngood+=asic2_obj.ngood()
        npix+=asic2_obj.NPIXELS
    subttl=asic1_subttl+'\n'+asic2_subttl
    if asic1_data or asic2_data:
        subttl+='\nbad pixels in black background. %i good pixels out of %i = %.1f%%' % (ngood,npix,100.0*ngood/npix)
        subttl+='\nV$_\mathrm{turnover}$ from red to blue (%.1fV to %.1fV)' % (lutmin,lutmax)
    fig.suptitle(subttl,fontsize=fontsize)


    for row in range(nrows):
        for col in range(ncols):
            TES=0
            ax[row,col].get_xaxis().set_visible(False)
            ax[row,col].get_yaxis().set_visible(False)
            #ax[row,col].set_xlim([0,1])
            #ax[row,col].set_ylim([0,1])

            # the pixel identity associated with its physical location in the array
            physpix=asic1_obj.pix_grid[row,col]
            pix_index=physpix-1
            face_colour='black'
            label_colour='white'

            text_y=0.5
            text_x=0.5
            if physpix==0:
                pix_label=''
                label_colour='black'
                face_colour='black'

            elif physpix in asic1_obj.TES2PIX[0]:
                TES=asic1_obj.pix2tes(physpix)
                TES_index = TES - 1
                pix_label=str('%i' % TES)
                label_colour='yellow'
                face_colour='blue'
                if asic1_data:
                    fontsize=asic1_fontsize
                    Iadjusted=asic1_obj.adjusted_iv(TES)
                    turnover=asic1_obj.turnover(TES)
                    text_x=max(asic1_obj.vbias)
                    text_y=min(Iadjusted)
                    curve_colour='black'
                    if (asic1_obj.is_good_iv(TES) is not None) and (not asic1_obj.is_good_iv(TES)):
                        face_colour='black'
                        label_colour='white'
                        curve_colour='white'
                    else:
                        face_colour=mylut(turnover,lutmin,lutmax)
                    asic1_obj.draw_iv(Iadjusted,colour=curve_colour,axis=ax[row,col])
                elif asic1_mapdata:
                    face_colour = mylut(a1[TES_index],lutmin,lutmax)

            elif physpix in asic2_obj.TES2PIX[1]:
                TES=asic2_obj.pix2tes(physpix)
                TES_index = TES - 1
                pix_label=str('%i' % TES)
                label_colour='black'
                face_colour='green'
                if asic2_data:
                    fontsize=asic2_fontsize
                    Iadjusted=asic2_obj.adjusted_iv(TES)
                    turnover=asic2_obj.turnover(TES)
                    text_x=max(asic2_obj.vbias)
                    text_y=min(Iadjusted)
                    curve_colour='blue'
                    if (asic2_obj.is_good_iv(TES) is not None) and (not asic2_obj.is_good_iv(TES)):
                        face_colour='black'
                        label_colour='white'
                        curve_colour='white'
                    else:
                        face_colour=mylut(turnover,lutmin,lutmax)
                    asic2_obj.draw_iv(Iadjusted,colour=curve_colour,axis=ax[row,col])
                elif asic2_mapdata:
                    face_colour = mylut(a2[TES_index],lutmin,lutmax)

            else:
                pix_label='???'
                label_colour='blue'
                face_colour='yellow'
                
            ax[row,col].set_facecolor(face_colour)
            ax[row,col].text(text_x,text_y,pix_label,va='center',ha='center',color=label_colour,fontsize=fontsize)
            
    plt.savefig(pngname,format='png',dpi=100,bbox_inches='tight')
    if xwin: plt.show()
    else: plt.close('all')

    return

'''
if __name__=="__main__":
    plot_physical_layout()
'''

