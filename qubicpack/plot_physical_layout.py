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

def plot_physical_layout(a1=None,a2=None,figsize=(16,16),xwin=True):
    '''
    plot an image of the TES array labeling each pixel
    plot the I-V curves in the appropriate boxes if a1 and/or a2 given
    '''

    obj_list=[a1,a2]
    asic1_obj=None
    asic2_obj=None
    for obj in obj_list:
        if isinstance(obj,qp):
            if obj.asic==1:
                asic1_obj=obj
            elif obj.asic==2:
                asic2_obj=obj
            else:
                print('PROBLEM! QubicPack object does not have a valid ASIC definition')
                return None

        
    if asic1_obj==None:
        asic1_obj=qp()
        asic1_obj.assign_asic(1)
        asic1_fontsize=figsize[0]
    if asic2_obj==None:
        asic2_obj=qp()
        asic2_obj.assign_asic(2)
        asic2_fontsize=figsize[0]

    asic1_data=True
    asic1_fontsize=8
    asic2_data=True
    asic2_fontsize=8
    if not isinstance(asic1_obj.adu,np.ndarray):
        asic1_data=False
        asic1_fontsize=figsize[0]
    if not isinstance(asic2_obj.adu,np.ndarray):
        asic2_data=False
        asic2_fontsize=figsize[0]
            
    asic1_obj.figsize=figsize
    fontsize=figsize[0]
    ttlfontsize=figsize[0]*1.2

    nrows=asic1_obj.pix_grid.shape[0]
    ncols=asic1_obj.pix_grid.shape[1]

    if xwin: plt.ion()
    else: plt.ioff()
    fig,ax=plt.subplots(nrows,ncols,figsize=asic1_obj.figsize)
    fig.text(0.5,0.985,'QUBIC TES array',ha='center',fontsize=ttlfontsize)
    pngname='TES_ARRAY.png'
    if xwin: fig.canvas.set_window_title('plt:  QUBIC TES array')

    asic1_subttl='Array %s ASIC1 blue background' % asic1_obj.detector_name
    asic2_subttl='Array %s ASIC2 green background' % asic2_obj.detector_name
    ngood=0
    if asic1_data:
        asic1_subttl+=asic1_obj.obsdate.strftime(', data from %Y-%m-%d %H:%M')
        ngood+=asic1_obj.ngood()
    if asic2_data:
        asic2_subttl+=asic2_obj.obsdate.strftime(', data from %Y-%m-%d %H:%M')
        ngood+=asic2_obj.ngood()
    subttl=asic1_subttl+'\n'+asic2_subttl
    if asic1_data or asic2_data:
        subttl+='\nbad pixels in red background. %i good pixels.' % ngood
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
            
            text_y=0.5
            text_x=0.5
            if physpix==0:
                pix_label=''
                label_colour='black'
                face_colour='black'

            elif physpix in asic1_obj.TES2PIX[0]:
                TES=asic1_obj.pix2tes(physpix)
                pix_label=str('%i' % TES)
                label_colour='white'
                face_colour='blue'
                if asic1_data:
                    fontsize=asic1_fontsize
                    Iadjusted=asic1_obj.adjusted_iv(TES)
                    text_x=max(asic1_obj.vbias)
                    text_y=min(Iadjusted)
                    asic1_obj.draw_iv(Iadjusted,colour='yellow',axis=ax[row,col])
                    if (not asic1_obj.is_good_iv(TES)==None) and (not asic1_obj.is_good_iv(TES)):
                        face_colour='red'
                        label_colour='white'

            elif physpix in asic2_obj.TES2PIX[1]:
                TES=asic2_obj.pix2tes(physpix)
                pix_label=str('%i' % TES)
                label_colour='white'
                face_colour='green'
                if asic2_data:
                    fontsize=asic2_fontsize
                    Iadjusted=asic2_obj.adjusted_iv(TES)
                    text_x=max(asic1_obj.vbias)
                    text_y=min(Iadjusted)
                    asic2_obj.draw_iv(Iadjusted,colour='blue',axis=ax[row,col])
                    if (not asic2_obj.is_good_iv(TES)==None) and (not asic2_obj.is_good_iv(TES)):
                        face_colour='red'
                        label_colour='white'

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

