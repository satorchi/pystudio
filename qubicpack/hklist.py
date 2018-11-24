#!/usr/bin/env python
'''
$Id: hklist.py
$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
$created: Wed 24 Oct 2018 14:46:23 CEST
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

numpy record array of all the QUBIC housekeeping
'''

def make_HKrecords(fname):
    '''
    make the Housekeeping records
    '''

    h=open(fname,'r')
    lines=h.read().split('\n')
    h.close()
    records_list=[]
    for line in lines:
        if line.find('#headings:')==0:
            headings=line.replace('#headings:','').split(',')
        elif line!='' and line[0]!='#':
            rec=line.split(',')
            records_list.append(rec)
    headings_fmt='index'
    nheadings=len(headings)
    fmts_template='i2'
    for heid in headings:
        headings_fmt+=','+heid.strip()
        fmts_template+=',a%i'
        
    nrecords=len(records_list)
    rec_len=len(rec)
    field_len=[]
    for idx in range(rec_len):  field_len.append(0)
    for rec in records_list:
        for idx,val in enumerate(rec):
            if len(val.strip())>field_len[idx]:
                field_len[idx]=len(val.strip())

    fmts=fmts_template % tuple(field_len)
    records=np.recarray(formats=fmts,names=headings_fmt,shape=(nrecords))
    for idx,rec in enumerate(records_list):
        entry=[]
        for val in rec:
            newval=val.strip(' ')
            entry.append(newval)
        record=tuple([idx]+entry)
        records[idx]=record
    return records

def make_wikiHKlist(records,filename=None):
    '''
    make a list of housekeeping compatible with pmwiki
    '''

    headings=records.dtype.names
    headline=''
    fmtline=''
    for heading in headings:
        headline+='||! {+%s+}  ' % heading
        fmt=str(records[heading].dtype)
        if fmt.find('int')>=0:
            fmtline+='||%03i'
        elif fmt.find('S')>=0:
            nchars=fmt.replace('|','%').replace('S','')+'s'
            fmtline+='||%s' % nchars 
        else:
            fmtline+='||%s'
            
    headline+='||\n'
    fmtline+='||\n'
    txt ='!QUBIC Housekeeping List\n\n\n'
    txt+='||! !||\n'
    txt+='||border=1 width=100%\n'
    txt+=headline
    for rec in records:
        line=fmtline % rec.astype(tuple)
        txt+=line

    if filename is not None:
        h=open(filename,'w')
        h.write(txt)
        h.close()

    return txt
