# Generate a TES I-V test report

### make_iv_tex_report()
This method will generate a LaTeX source file which will include a summary table of all TES I-V curves and plots of each one.  There will also be a plot of all the TES, each in its corresponding location on the focal plane (see plot_iv_physical_layout() in the [Plotting section](../Data-Plotting)).  All the plots should be generated before running _pdflatex_ on this file.  To make things easier, use the method _make_iv_report()_ described below.

### make_iv_report()
This method will generate all that is necessary to make the test report.  This includes running the _filter_ if not already done, generating all the required plots, generating the LaTeX source file, and compiling the LaTeX file with _pdflatex_.  The result is a **PDF** document of around 70 pages, with all the information mentioned in *make_iv_tex_report()* described above.
