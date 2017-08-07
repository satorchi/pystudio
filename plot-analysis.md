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

filter_iv_all()
 * run a filter on the I-V data to determine which are good pixels

