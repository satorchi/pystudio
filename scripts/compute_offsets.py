'''
$Id: compute_offsets.py
$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
$created: Fri 15 Dec 2017 17:58:35 CET
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

this is a translation of the Dscript: Comp_offset_ASIC1b.dscript
once tested, it will be moved into qubicpack acquisition.py

'''
from qubicpack import qubicpack as qp
import numpy as np


#go=qp()
#go.assign_asic(1)

client=go.connect_QubicStudio()
if client==None:quit()
go.assign_integration_time(1.0)


k=0.2
imax=10   
consigne=0 # what's this?

offsets = np.zeros(go.NPIXELS)

for counter in range(imax):

    print('count: %i/%i',(counter+1,imax))
    timeline = go.integrate_scientific_data()
    data_avg=timeline.mean(axis=-1)
    for pix_index in range(go.NPIXELS):
        pix=pix_index+1
	offsets[pix_index]+=k*(data_avg[pix_index]-consigne)
        
    client.sendSetOffsetTable(go.QS_asic_index, offsets)
    go.wait_a_bit()



