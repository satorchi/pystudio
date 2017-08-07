# Methods used for data acquisition

wait_a_bit(pausetime=0.3)
 * pause before continuing.  The default is 0.3 seconds.
 
make_Vbias(cycle_voltage=True,vmin=5.0,vmax=8.0,dv=0.04,lowhigh=True):
 - make the list of bias voltages used during the I-V curve measurement
 
get_iv_data()
 * run an I-V measurement
 * see also the wrapper script run_iv.py in the [example scripts](https://github.com/satorchi/pystudio/tree/master/scripts)

connect_QubicStudio(ip=None)
 * connect to QubicStudio
 * the optional keyword ip can be used to specifiy the IP address of the QubicStudio machine
