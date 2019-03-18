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

cc_datadir  = '/sps/hep/qubic/Data/Calib-TD'
qs_datadir  = '/qs/Qubic Studio/backup'
cs_datadir  = '/calsource/qubic'
jup_datadir = '/qubic/Data/Calib-TD'

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

def archive_command(server,archive_cmd):
    '''
    run a command via ssh on the archive server (either cc or apcjupyter)
    '''
    cmd = 'ssh %s "%s"' % (server,archive_cmd)
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


def files_on_QubicStudio():
    '''
    find all the data files on QubicStudio
    '''
    glob_pattern = '%s/20??-??-??/*/*/*.fits' % qs_datadir
    qs_filelist = glob(glob_pattern)
    qs_filelist.sort()

    qs_filelist_relative = make_relative_filelist(qs_datadir,qs_filelist)
    
    return qs_filelist,qs_filelist_relative

def files_on_calsource():
    '''
    find all the data files on calsource
    '''
    glob_pattern = '%s/calsource_*.dat' % cs_datadir
    cs_filelist = glob(glob_pattern)
    cs_filelist.sort()
    cs_filelist_relative = make_relative_filelist(cs_datadir,cs_filelist)
    # files on cc are in the calsource subdirectory
    for idx,f in enumerate(cs_filelist_relative):
        cs_filelist_relative[idx] = 'calsource/'+f

    return cs_filelist, cs_filelist_relative

def files_on_archive(server):
    '''
    find the files already on the archive (either cc or jupyter)
    '''
    datadir = None
    if server=='cc':
        datadir = cc_datadir
    if server=='apcjupyter':
        datadir = jup_datadir
    if datadir is None: return None
        
    cmd = 'find %s -type f \\( -name "*.fits" -o -name "*.dat" \\)' % datadir
    out,err = archive_command(server,cmd)
    if err:
        print(err)

    filelist = out.split('\n')
    filelist_relative = make_relative_filelist(datadir,filelist)
    return filelist, filelist_relative
    

def copy2archive(server):
    '''
    copy data files to CC-IN2P3 or to apcjupyter
    '''
    archive_datadir = None
    if server=='cc':
        archive_datadir = cc_datadir
    if server=='apcjupyter':
        archive_datadir = jup_datadir
    if archive_datadir is None:
        print('Invalid archive.  Choose either "apcjupyter" or "cc"')
        return

    
    # files on Qubic Studio
    src_list, qs_filelist_relative = files_on_QubicStudio()
    
    # files on the calsource
    cs_filelist, cs_filelist_relative = files_on_calsource()
    src_list += cs_filelist
    
    # files on archive
    archive_filelist, archive_filelist_relative = files_on_archive(server)

    # now check what is new
    destfiles2copy = []
    srcfiles2copy = []
    for idx,f in enumerate(qs_filelist_relative+cs_filelist_relative):
        if f not in archive_filelist_relative:
            destfiles2copy.append(f)
            srcfiles2copy.append(src_list[idx])

    if not destfiles2copy:
        return

    # we need to create the destination directories before copying the file
    for idx,f in enumerate(destfiles2copy):

        dest_fullpath = '%s/%s' % (archive_datadir,f)
        print('file destination:\n   %s' % dest_fullpath)
        d = os.path.dirname(dest_fullpath)
        print('directory to be made:\n   %s' % d)
        escaped_d = d.replace(' ','\\ ')
        cmd = 'mkdir --parents %s' % escaped_d
        out,err = archive_command(server,cmd)
        if err:
            print(err)
            return
        if out:
            print(out)

        escaped_destination = dest_fullpath.replace(' ','\\ ')
        src_file = srcfiles2copy[idx]
        cmd = 'scp -p "%s" %s:"%s"' % (src_file,server,escaped_destination)
        #print('copy command:\n   %s' % cmd)
        out,err = shell_command(cmd)
        if err:
            print(err)
            return
        if out:
            print(out)
    return

def copy2cc():
    '''
    copy files to CC-IN2P3
    '''
    return copy2archive('cc')

def copy2jup():
    '''
    copy files to apcjupyter
    '''
    return copy2archive('apcjupyter')
    

