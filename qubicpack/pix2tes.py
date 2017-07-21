'''
$Id: pix2tes.py
$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
$created: Fri 21 Jul 2017 08:26:39 CEST
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

translate the TES number to the physical location on focal plane grid
'''
import numpy as np

def assign_TES_grid(self):
    '''
    generate the layout of the TES array
    zeros indicate empty grid positions
    '''
    ncols=[8,9,11,12,12,14,15,15,16,17,17,17,17,17,17,17,17]
    rows=[]
    prev_row_end=0
    for N in ncols:
        row=np.arange(N)+prev_row_end+1
        rows.append(row)
        prev_row_end=row[-1]

    full_grid=np.zeros((17,17), dtype=int)
    nrow=0
    for row in rows:
        Ntes=len(row)
        full_grid[nrow,0:Ntes]=row
        nrow+=1

    self.TES_grid=full_grid
    return full_grid

def assign_pix2tes(self):
    pix2tes=[]

    # asic 1
    pix2tes.append([125,126,127,128,121,122,123,124,117,118,119,120,113,114,115,116,109,110,111,112,105,106,107,108,101,102,103,104,97,98,99,100,93,94,95,96,89,90,91,92,85,86,87,88,81,82,83,84,77,78,79,80,73,74,75,76,69,70,71,72,65,66,67,68,61,62,63,64,57,58,59,60,53,54,55,56,49,50,51,52,45,46,47,48,41,42,43,44,37,38,39,40,33,34,35,36,29,30,31,32,25,26,27,28,21,22,23,24,17,18,19,20,13,14,15,16,9,10,11,12,5,6,7,8,1,2,3,4])

    # asic 2
    pix2tes.append([29,30,31,32,25,26,27,28,21,22,23,24,17,18,19,20,13,14,15,16,9,10,11,12,5,6,7,8,1,2,3,4,61,62,63,64,57,58,59,60,53,54,55,56,49,50,51,52,45,46,47,48,41,42,43,44,37,38,39,40,33,34,35,36,93,94,95,96,89,90,91,92,85,86,87,88,81,82,83,84,77,78,79,80,73,74,75,76,69,70,71,72,65,66,67,68,125,126,127,128,121,122,123,124,117,118,119,120,113,114,115,116,109,110,111,112,105,106,107,108,101,102,103,104,97,98,99,100])

    self.pix2tes=np.array(pix2tes)
    return
