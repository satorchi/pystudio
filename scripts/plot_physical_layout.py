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


def plot_physical_layout(xwin=True,figsize=(16,16)):
    '''
    plot an image of the TES array labeling each pixel
    '''
    go=qp()
    go.figsize=figsize
    fontsize=figsize[0]
    ttlfontsize=fontsize*1.2
    
    ttl='QUBIC TES array\nASIC1 in blue.  ASIC2 in green.'
    
    nrows=go.pix_grid.shape[0]
    ncols=go.pix_grid.shape[1]

    if xwin: plt.ion()
    else: plt.ioff()
    fig,ax=plt.subplots(nrows,ncols,figsize=go.figsize)
    pngname='TES_ARRAY.png'
    if xwin: fig.canvas.set_window_title('plt:  '+ttl)
    fig.suptitle(ttl,fontsize=ttlfontsize)
    

    TES_translation_table_ASIC1=go.TES2PIX[0]
    TES_translation_table_ASIC2=go.TES2PIX[1]

    for row in range(nrows):
        for col in range(ncols):
            TES=0
            ax[row,col].get_xaxis().set_visible(False)
            ax[row,col].get_yaxis().set_visible(False)
            ax[row,col].set_xlim([0,1])
            ax[row,col].set_ylim([0,1])

            # the pixel identity associated with its physical location in the array
            physpix=go.pix_grid[row,col]
            pix_index=physpix-1
            
            text_y=0.5
            text_x=0.5
            if physpix==0:
                pix_label=''
                label_colour='black'
                face_colour='black'
            elif physpix in TES_translation_table_ASIC1:
                go.assign_asic(1)
                TES=go.pix2tes(physpix)
                pix_label=str('%i' % TES)
                label_colour='white'
                face_colour='blue'
            elif physpix in TES_translation_table_ASIC2:
                go.assign_asic(2)
                TES=go.pix2tes(physpix)
                pix_label=str('%i' % TES)
                label_colour='white'
                face_colour='green'
            else:
                pix_label='???'
                label_colour='blue'
                face_colour='yellow'
                
            ax[row,col].set_axis_bgcolor(face_colour)
            ax[row,col].text(text_x,text_y,pix_label,va='center',ha='center',color=label_colour,fontsize=fontsize)
            
    plt.savefig(pngname,format='png',dpi=100,bbox_inches='tight')
    if xwin: plt.show()
    else: plt.close('all')

    return

if __name__=="__main__":
    plot_physical_layout()

    return

