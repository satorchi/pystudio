# Methods used for data acquisition

### connect_QubicStudio(ip=None)
connect to QubicStudio.  The default behaviour is to check first if there is already a connection, and then to use that connection.  The return value *client* can be used in subsequent calls to QubicStudio.
 * the optional keyword ip can be used to specifiy the IP address of the QubicStudio machine.  The default is the LaboMM machine.

### wait_a_bit(pausetime=0.3)
Pause before continuing.  The default is 0.3 seconds.
 
### make_Vbias(cycle_voltage=True,ncycles=1, vmin=5.0,vmax=8.0,dv=0.04,lowhigh=True)
make the list of bias voltages used during the I-V curve measurement.  Optional keywords are the following:
* vmin: low end of the bias range
* vmax: high end of the bias range
* dv: step size of voltage increments/decrements
* cycle_voltage: cycle the voltage back to the starting value (from low to high to low, or the reverse).  
* ncycles: the number of I-V cycles.  Note, if cycling the voltage back to the starting value, a single cycle will give you two I-V curves, one going up, and one going down.
* lowhigh:  vary the bias voltage from low to high (default is True).  If False, the bias voltage begins at the high end and reduces to the lowest value.

 
### get_iv_data()
 * run an I-V measurement
 * see also the wrapper script run_iv.py in the [example scripts](https://github.com/satorchi/pystudio/tree/master/scripts)
