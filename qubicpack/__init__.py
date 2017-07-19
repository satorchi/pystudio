"""
$Id: __init__.py<qubicpack>
$auth: Steve Torchinsky <satorchi@apc.in2p3.fr>

$created: Mon 10 Jul 2017 11:55:24 CEST
$license: GPLv3 or later, see https://www.gnu.org/licenses/gpl-3.0.txt

          This is free software: you are free to change and
          redistribute it.  There is NO WARRANTY, to the extent
          permitted by law.

a class with tools which are generally useful for scripts using pystudio
"""
from __future__ import division, print_function
import numpy as np
import pystudio
import sys,os,time
import datetime as dt
import matplotlib.pyplot as plt
from glob import glob

class qubicpack:

    from .assign_variables import\
        assign_defaults,\
        assign_observer,\
        assign_asic,\
        asic_index,\
        TES_index,\
        assign_integration_time,\
        assign_Vtes,\
        assign_pausetime
    
    from .tools import\
        connect_QubicStudio,\
        read_date_from_filename,\
        write_fits,\
        read_fits,\
        get_amplitude,\
        get_mean,\
        integrate_scientific_data,\
        set_VoffsetTES,\
        set_diffDAC,\
        set_slowDAC

    from .iv import\
        wait_a_bit,\
        ADU2I,\
        find_normalization,\
        find_offset,\
        setup_plot_Vavg,\
        plot_Vavg,\
        plot_iv_all,\
        plot_iv_multi,\
        make_line,\
        fit_iv,\
        draw_iv,\
        plot_iv,\
        make_Vbias,\
        get_Vavg_data,\
        filter_Vtes,\
        read_Vtes_file,\
        heres_one_I_made_earlier

    from .ASD import\
        plot_ASD
    
    def __init__(self):
        self.assign_defaults()
        return

    def verdate(self):
        print("Thu 13 Jul 2017 15:54:22 CEST")
        return

