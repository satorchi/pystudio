# Plotting I-V and related curves
The plotting routines all have an option _xwin_ which can be set to _True_ or _False_.  If _xwin=False_ then the plot is not shown on screen but is simply saved to a png file.

### plot_iv(TES=None,offset=None,multi=False)
make a plot of an I-V curve, or multiple curves
 - if TES=None, all I-V curves are plotted on top of each other
 - if multi=True, a grid of plots is made, one for each TES
 - see also plot_iv_physical_layout() below

### plot_iv_physical_layout(xwin=True)
plot the I-V curves in thumbnails mapped to the physical location of each detector
 * the optional keyword xwin can be set to False and the plot will not appear on screen but will only be saved to a png file.

If you would like to plot the I-V curves from both ASICs on a single plot, you should use the [standalone version](plot_physical_layout.md).

### plot_iv_all(selection=None)
plot all the I-V curves on top of each other.  The optional parameter *selection* is used to make a selection of curves to plot. Enter a list of True/False for each TES.  You can get such a list using the method *is_good_iv()* (see [analysis routines](Data-analysis)).


