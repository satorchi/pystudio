#!/usr/bin/env python
'''
$Id: copy_data.py
$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
$created: Fri 15 Feb 2019 07:48:49 CET
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

copy QUBIC data to cc-in2p3.  
This script is run on qubic-central (192.168.2.1) which has access to the QubicStudio files via Samba
'''
from __future__ import division, print_function
import sys,os,time,subprocess
from glob import glob

def shell_command(cmd):
    '''
    run a shell command and retrieve the output
    '''
    print('command shell:\n   %s' % cmd)
    proc=subprocess.Popen(cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out,err = proc.communicate()
    return out,err

def cc_command(cc_cmd):
    '''
    run a command on cc-in2p3 via ssh
    '''
    cmd = 'ssh cc "%s"' % cc_cmd
    return shell_command(cmd)

def make_relative_filelist(datadir,filelist):
    '''
    make a list of relative filenames (strip the absolute path)
    '''
    filelist_relative = []
    delete_txt = '%s/' % datadir
    for f in filelist:
        filelist_relative.append(f.replace(delete_txt,''))
    return filelist_relative
    

def copy2cc():
    '''
    copy data files to CC-IN2P3
    '''
    
    cc_datadir = '/sps/hep/qubic/Data/Calib-TD'
    qs_datadir = '/qs/Qubic Studio/backup'
    cs_datadir = '/calsource/qubic'

    # files on the calsource
    glob_pattern = '%s/calsource_*.dat' % cs_datadir
    cs_filelist = glob(glob_pattern)
    cs_filelist_relative = make_relative_filelist(cs_datadir,cs_filelist)

    # files on Qubic Studio
    glob_pattern = '%s/20??-??-??/*/*/*.fits' % qs_datadir
    qs_filelist = glob(glob_pattern)
    qs_filelist_relative = make_relative_filelist(qs_datadir,qs_filelist)

    # files on CC
    cmd = 'find %s -type f -name "*.fits"' % cc_datadir
    out,err = cc_command(cmd)
    if err:
        print(err)

    cc_filelist = out.split('\n')
    cc_filelist_relative = make_relative_filelist(cc_datadir,cc_filelist)

    # now check what is new
    files2copy = []
    for f in qs_filelist_relative+cs_filelist_relative:
        if f not in cc_filelist_relative:
            files2copy.append(f)

    if not files2copy:
        return

    # we need to create the destination directories before copying the file
    for f in files2copy:

    # for a test, just do the first one
    #f = files2copy[0]
    #print('testing with file:\n   %s' % f)
    
        dest_fullpath = '%s/%s' % (cc_datadir,f)
        print('file destination:\n   %s' % dest_fullpath)
        d = os.path.dirname(dest_fullpath)
        print('directory to be made:\n   %s' % d)
        escaped_d = d.replace(' ','\\ ')
        cmd = 'mkdir --parents %s' % escaped_d
        out,err = cc_command(cmd)
        if err:
            print(err)
            return
        if out:
            print(out)

        escaped_destination = dest_fullpath.replace(' ','\\ ')
        cmd = 'scp -p "%s/%s" cc:"%s"' % (qs_datadir,f,escaped_destination)
        #print('copy command:\n   %s' % cmd)
        out,err = shell_command(cmd)
        if err:
            print(err)
            return
        if out:
            print(out)
    return

        
if __name__=='__main__':
    copy2cc()
    

