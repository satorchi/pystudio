wait_a_bit(pausetime=0.3)
 * pause before continuing.  The default is 0.3 seconds.
 
ADU2I(ADU, offset=None)
 * conversion from the Analogue Digital Units returned by QubicStudio to current in micro Ampere
 * the optional offset will raise/lower the entire curve.  Note that in general, offset is calculated by methods such as plot_iv() (see below).

plot_iv(TES=None,offset=None,multi=False)
 - make a plot of an I-V curve, or multiple curves
 - if TES=None, all I-V curves are plotted on top of each other
 - if multi=True, a grid of plots is made, one for each TES
 - see also plot_iv_physical_layout() below

plot_iv_physical_layout(xwin=True)
 * plot the I-V curves in thumbnails mapped to the physical location of each detector
 * the optional keyword xwin can be set to False and the plot will not appear on screen but will only be saved to a png file.
 
make_Vbias(cycle_voltage=True,vmin=5.0,vmax=8.0,dv=0.04,lowhigh=True):
 - make the list of bias voltages used during the I-V curve measurement
 
get_iv_data()
 * run an I-V measurement
 * see also the wrapper script run_iv.py in the [example scripts](https://github.com/satorchi/pystudio/tree/master/scripts)

filter_iv_all()
 * run a filter on the I-V data to determine which are good pixels

connect_QubicStudio(ip=None)
 * connect to QubicStudio
 * the optional keyword ip can be used to specifiy the IP address of the QubicStudio machine
