#!/usr/bin/env python
'''
$Id: make_translation_table.py
$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
$created: Wed 02 Aug 2017 07:50:14 CEST
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

make a translation table with correspinding values for:
  ASIC number
  PIX number
  TES number
  Open loop test results
  Room temperature test results

'''
from __future__ import division, print_function
import sys,os,time
import datetime as dt
from qubicpack import qubicpack as qp
import pickle

def read_txtcolumns(filename):
    if not os.path.exists(filename):
        print('ERROR! file not found: %s' % filename)
        return None
    h=open(filename,'r')
    raw=h.read()
    h.close()

    # remove empty lines, and create a 2d list for the rows & columns
    ret=[]
    lines=raw.split('\n')
    idx=0
    for line in lines:
        if line=='':
            del(lines[idx])
            continue
        val=line.split()
        ret.append(val)
        idx+=1
    return ret

def assign_openloop_results(transdic,asic):
    '''
    add the Open Loop test results for ASICn
    '''
    go=qp()
    go.assign_asic(asic)
    asic_transdic=[entry for entry in transdic if entry['ASIC'] == asic]
    filename=str('P73_openlooptest_asic%i.txt' % asic)
    OpenLoopList=read_txtcolumns(filename)
    for val in OpenLoopList:
        TES=int(eval(val[0]))
        if val[1]=='0':
            OL='open'
        elif val[1]=='S':
            OL='supra'
        elif val[1]=='1':
            OL='good'        
        else:
            OL=val[1]

        # find the corresponding entry in the list
        TESlist=[entry['TES'] for entry in asic_transdic]
        npts=len(TESlist)
        gotit=False
        idx=0
        while (not gotit) and (idx<npts):
            _TES=TESlist[idx]
            if _TES==TES:
                gotit=True
                entry_idx=idx
            idx+=1
            
        if gotit:
            entry=asic_transdic[entry_idx]
        else:
            transdic.append({})
            entry=transdic[-1]
        entry['OpenLoop']=OL
    
    return transdic

def make_translation_table():
    go=qp()
    transdic=[]
    
    RTlist=read_txtcolumns('P73_room_temperature.txt')
    npts_rt=len(RTlist)
    for val in RTlist:
        entry={}
        PIX=int(eval(val[0]))
        entry['PIX']=PIX
        try:
            entry['R300']=eval(val[1])
        except:
            if val[1]=='HS':
                entry['R300']='open'
            else:
                entry['R300']=val[1]

        if PIX in go.TES2PIX[0,:]:
            asic=1
        elif PIX in go.TES2PIX[1,:]:
            asic=2
        else:
            entry['TES']=-1
            entry['ASIC']=-1
            transdic.append(entry)
            continue

        go.assign_asic(asic)
        TES=go.pix2tes(PIX)
        entry['TES']=TES
        entry['ASIC']=asic
        transdic.append(entry)

    transdic=assign_openloop_results(transdic,1)
    transdic=assign_openloop_results(transdic,2)

    # make sure all entries have all keys
    allkeys=['TES','PIX','ASIC','R300','OpenLoop']
    nkeys=len(allkeys)
    for entry in transdic:
        for key in allkeys:
            if not key in entry:
                entry[key]='no data'

    return transdic

if __name__ == '__main__':
    transdic=make_translation_table()
    h=open('TES_translation_table.pickle','w')
    pickle.dump(transdic,h)
    h.close()
    
