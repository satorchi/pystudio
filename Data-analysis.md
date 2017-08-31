# Data analysis methods

### ADU2I(ADU, offset=None)
conversion from the Analogue Digital Units returned by QubicStudio to current in micro Ampere
 * the optional offset will raise/lower the entire curve.  Note that in general, offset is calculated by methods such as plot_iv() (see below).  If you want to have the vector of points for an I-V curve, you can use the method *Ites()* described below.

### adjusted_iv(TES)
return a vector with the measured current for each bias point.  This is the current measured in &mu;A. If you want the corresponding bias voltages, they can be found in the variable *vbias*.  For example, if your QubicPack object is called *go*, then the bias voltages are found in *go.vbias*
You might prefer to use the method *Ites* described below.

### Ites(TES)
return the measured current in Amps (not &mu;Amps).

### Vtes(TES)
return the voltage across the TES.  This is *not* the bias voltage.  *Vtes* is calculated according to:

```
Vtes=Rshunt*(vbias/Rbias-Ites)
```

with:
* Rshunt=0.01 &Omega;
* Rbias=10000 &Omega;

### Ptes(TES)
return the power across the TES which is simply _Ites * Vtes_

### Rn_ratio(TES)
the ratio of TES resistance to Normal Resistance (see __R1__ below).



### filter_iv(TES,residual_limit=3.0,abs_amplitude_limit=0.01,rel_amplitude_limit=0.1,bias_margin=0.2,jumplimit=2.0)
This method will apply a filter to the I-V curve of a given TES, and determine if this is a good pixel.  The I-V curve is fit to a 3rd degree polynomial in order to find the turnover (operation) point of the TES.  The dynamic normal resistance (resistance at high bias voltage) which should be on the order of 1 Ohm, is determined by fitting the final points to a straight line.  

arguments:
 * **TES** is the TES number (required)
 * the remaining keywords are all optional:
   * **residual_limit**: this is an indication of the acceptable quality of the polynomial fit
   * **abs_amplitude_limit**: this is the lower limit for acceptable current measured
   * **real_amplitude_limit**: this is the lower limit for the peak-to-peak variation in the measured current across the bias voltage range applied.
   * **bias_margin**: this is the proximity to the edge of the bias range which is considered to be acceptable
   * **jump_limit**: this is the current step size between bias points which is considered to be a jump.  The polynomial fit takes this into account when it determines which points to fit.

### filter_iv_all(residual_limit=3.0,abs_amplitude_limit=0.01,rel_amplitude_limit=0.1,bias_margin=0.2,jumplimit=2.0)
 * run a filter on the I-V data to determine which are good pixels.  The keywords are as described above for filter_iv().  The result is stored in the qubicpack object and is used in subsequent plotting.  The filter results are accessible via a number of helper methods, or directly in the python list called _filtersummary_.

### is_good_iv(TES)
The return value is the determination of whether or not the TES is considered to be a good pixel.  If no TES is specified, the return value is a list of True/False values corresponding to the evaluation of each TES.

### ngood()
The return value is the total number of good pixels.

### good_index()
The return value is a list of indexes corresponding to the TES which are considered to be good.  **WARNING!!!** These indexes are not the same as the TES number!  TES_index=TES-1 (python counts starting from zero).  In general, wherever the word *index* is used, it refers to a count which begins at zero.

### R1(TES)
The return value is the Dynamic Normal Resistance of the TES.  This should be close to 1 Ohm.  If no TES is specified, the return value is a list corresponding to the calculated R1 value of each TES.

### turnover(TES)
The return value is the turnover (operating) point of the TES.    If no TES is specified, the return value is a list corresponding to the calculated turnover point of each TES.

### offset(TES)
The return value is the current offset used to make the I-V curve intersect with the R=1 Ohm line at the highest bias voltage.  If no TES is specified, the return value is a list corresponding to the calculated offset of each TES.

