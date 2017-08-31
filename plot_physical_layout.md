# Plot all TES I-V curves on a map of the focal plane
This function allows you to plot the I-V curves from two ASIC on the same plot.

### plot_physical_layout(xwin=True,figsize=(16,16),a1=None,a2=None)
Options:
* xwin : *True* plot on the screen.
* figsize : a tuple with the size of the final output
* a1 : a qubicpack object containing the data from ASIC1
  * the default is to plot only the Pixel ID and no data
* a2 : a qubicpack object containing the data from ASIC2
  * the default is to plot on the Pixel ID and no data

Here is an example python script to make the plot:

```
from qubicpack import qubicpack as qp
from qubicpack.plot_physical_layout import *

a1=qp()
a1.read_fits('QUBIC_TES_20170711T151016UTC.fits')
a2=qp()
a2.read_fits('QUBIC_TES_20170712T154242UTC.fits')

ret=plot_physical_layout(a1=a1,a2=a2)
```
