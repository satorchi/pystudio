#! /usr/bin/env python

import hooks
import os,sys
from distutils.spawn import find_executable
from numpy.distutils.core import setup
from numpy.distutils.extension import Extension
import subprocess

DISTNAME         = 'pystudio'
DESCRIPTION      = 'Python interface for Qubic Studio'
AUTHOR           = 'Pierre Chanial'
AUTHOR_EMAIL     = 'pierre.chanial@gmail.com'
MAINTAINER       = 'Steve Torchinsky'
MAINTAINER_EMAIL = 'satorchi@apc.in2p3.fr'
URL              = 'https://github.com/satorchi/pystudio'
LICENSE          = 'GPL'
DOWNLOAD_URL     = 'https://github.com/satorchi/pystudio'
VERSION          = '2.0.0'
hooks.FILE_PREPROCESS = 'preprocess.py'
hooks.MIN_VERSION_CYTHON = '0.23'

with open('README.md') as f:
    long_description = f.readlines()

try:
    libdispatcheraccess = os.environ['LIBDISPATCHERACCESS']
except KeyError:
    libdispatcheraccess = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'lib')

qtpath = os.environ.get('QTPATH', '/usr/include/qt5')
if not os.path.exists(qtpath):
    if find_executable('pkg-config') is None:
        raise RuntimeError(
            'Either set the environment variable QTPATH to the Qt5 root includ'
            'e directory or install the pkg-config utility.')
    try:
        out = hooks.run(
            'pkg-config Qt5Core Qt5Network Qt5Widgets --cflags-only-I')
    except RuntimeError:
        raise RuntimeError('The Qt5 include directories could not be found.')
    qt_include = out[2:].split(' -I')
else:
    qt_include = [os.path.join(qtpath, _)
                  for _ in ('', 'QtCore', 'QtNetwork', 'QtWidgets')]

include_dirs = ['include', 'src'] + qt_include

libraries = ['dispatcheraccess',
             'dispatchertf',
             'Qt5Core',
             'Qt5Gui',
             ('helpers',
              {'language': 'c++',
               'sources': ['src/helpers.cpp'],
               'depends': ['src/helpers.h'],
               'include_dirs': include_dirs})]

setup(install_requires=['numpy'],
      name=DISTNAME,
      version=hooks.get_version(DISTNAME, VERSION),
      packages=[DISTNAME,'qubicpack'],
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
      cmdclass=hooks.cmdclass,
      ext_modules=[
          Extension('pystudio.pystudio',
                    ['pystudio/pystudio.pyx'],
                    language='c++',
                    depends=['pystudio/dispatcheraccess.pyx',
                             'pystudio/parameters.pyx',
                             'pystudio/paramscomputer.pyx',
                             'pystudio/requests.pyx',
                             'pystudio/libdispatcheraccess.pxd',
                             'pystudio/libhelpers.pxd',
                             'pystudio/libqt.pxd'],
                    libraries=libraries,
                    include_dirs=include_dirs,
                    library_dirs=[libdispatcheraccess],
                    runtime_library_dirs=[libdispatcheraccess]
          )
      ]
)


# add dispatcherAccess to executable path
if len(sys.argv)>1 and sys.argv[1]=='install':
    print 'copying dispatcher executables...'
    cmd='cp -puv pystudio/data/*.dispatcher /usr/bin;chown root:root /usr/bin/*.dispatcher;chmod 0755 /usr/bin/*.dispatcher'
    proc=subprocess.Popen(cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out,err=proc.communicate()
    if out!='':print out
    if err!='':print err

    
