#! /usr/bin/env python
'''
$Id: setup_qubicpack.py
$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>
$created: Mon 07 Aug 2017 08:35:24 CEST
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

setup.py for qubicpack only.  
Use this to install qubicpack without pystudio
'''
from __future__ import division, print_function
import os,sys,subprocess
from numpy.distutils.core import setup

DISTNAME         = 'qubicpack'
DESCRIPTION      = 'Utilities for QUBIC detector data visualization'
AUTHOR           = 'Steve Torchinsky'
AUTHOR_EMAIL     = 'satorchi@apc.in2p3.fr'
MAINTAINER       = 'Steve Torchinsky'
MAINTAINER_EMAIL = 'satorchi@apc.in2p3.fr'
URL              = 'https://github.com/satorchi/pystudio'
LICENSE          = 'GPL'
DOWNLOAD_URL     = 'https://github.com/satorchi/pystudio'
VERSION          = '2.0.0'

with open('README.md') as f:
    long_description = f.readlines()


setup(install_requires=['numpy'],
      name=DISTNAME,
      version=VERSION,
      packages=[DISTNAME, DISTNAME+'/hk'],
      package_data={DISTNAME: ['data/*']},
      zip_safe=False,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      maintainer=MAINTAINER,
      maintainer_email=MAINTAINER_EMAIL,
      description=DESCRIPTION,
      license=LICENSE,
      url=URL,
      download_url=DOWNLOAD_URL,
      long_description=long_description,
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Topic :: Scientific/Engineering'],
)

# install the executable scripts
exec_dir = '/usr/local/bin'
scripts = ['scripts/calsource_commander.py',
           'qubicpack/copy_data.py',
           'scripts/make_hk_fits.py',
           'scripts/modulator_commander.py',
           'scripts/run_bot.py',
           'scripts/run_hkserver.py',
           'scripts/copy2cc.py',
           'scripts/copy2jupyter.py']
if len(sys.argv)>1 and sys.argv[1]=='install':
    print('installing executable scripts...')
    for F in scripts:
        basename = os.path.basename(F)
        cmd = 'rm -f %s/%s; cp -puv %s %s;chmod +x %s/%s' % (exec_dir,F,F,exec_dir,exec_dir,basename)
        proc=subprocess.Popen(cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out,err=proc.communicate()
        if out:print(out.strip())
        if err:print(err.strip())

