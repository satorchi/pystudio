# Temperature Analysis of TES from I-V curves

The temperature analysis is done on a series of measurements at different bath temperature.  In order to use the routines, start your script with the following:

```
from qubicpack.temperature_analysis import *
```

You will then have access to the following routings:

### read_data_from_20170804()
read data from the test campaign of 2017-08-04 I-V curves of P73 at different bath temperatures

for example: 

```
data_list=read_data_from_20170804()
```

### plot_TES_temperature_curves(data_list,TES,plot='I',xwin=True)
plot the I-V, P-V, R-P curves for each temperature

arguments:
* *data_list* : the list of qubicpack objects with the I-V data
* *TES* : an integer between 1 and 128 identifying the TES
* *plot* : choose the plot type.  
   * plot='I' : I-V curves
   * plot='P' : P-V curves
   * plot='R' : R-P curves
* xwin : plot to screen, True or False.  If False, the plot will be saved to a png file, but not displayed on the screen
