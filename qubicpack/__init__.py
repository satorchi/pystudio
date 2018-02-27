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
import datetime as dt
import sys,os,time
import matplotlib.pyplot as plt

try:
    import pystudio
    with_pystudio=True
except:
    with_pystudio=False
    print('WARNING: importing qubicpack without pystudio')

    
class qubicpack:

    from .assign_variables import\
        assign_defaults,\
        assign_observer,\
        assign_asic,\
        asic_index,\
        TES_index,\
        assign_integration_time,\
        assign_ADU,\
        assign_pausetime,\
        assign_temperature,\
        assign_datadir,\
        assign_obsdate,\
        assign_bias_factor,\
        assign_detector_name,\
        guess_detector_name,\
        assign_logfile

    from .pix2tes import\
        assign_pix_grid,\
        assign_pix2tes,\
        tes2pix,\
        pix2tes,\
        assign_lookup_table,\
        lookup_TEStable
    
    from .tools import\
        read_date_from_filename,\
        write_fits,\
        read_fits,\
        read_bins,\
        output_filename,\
        data_subdir,\
        get_from_keyboard,\
        writelog

    from .iv import\
        exist_iv_data,\
        wait_a_bit,\
        lut,\
        n_masked,\
        ADU2I,\
        setup_plot_Vavg,\
        plot_Vavg,\
        plot_iv_all,\
        setup_plot_iv_multi,\
        plot_iv_multi,\
        plot_iv_physical_layout,\
        make_line,\
        filter_jumps,\
        polynomial_fit_parameters,\
        combined_fit_parameters,\
        do_polyfit,\
        do_combinedfit,\
        model_iv_super,\
        model_iv_mixed,\
        model_iv_normal,\
        model_iv_combined,\
        fit_iv,\
        draw_tangent,\
        fitted_iv_curve,\
        draw_iv,\
        setup_plot_iv,\
        adjusted_iv,\
        oplot_iv,\
        plot_iv,\
        plot_pv,\
        plot_rp,\
        make_Vbias,\
        filter_iv,\
        filter_iv_all,\
        read_filter,\
        save_filter,\
        filterinfo,\
        assign_filterinfo,\
        is_good_iv,\
        good_index,\
        ngood,\
        turnover,\
        offset,\
        R1adjust,\
        R1,\
        Rn,\
        selected_iv_curve,\
        Vtes,\
        Ites,\
        Ptes,\
        Rn_ratio,\
        Pbias,\
        read_ADU_file,\
        iv_tex_table_entry,\
        make_iv_tex_report,\
        make_iv_report,\
        iv2txt

    from .timeline import\
        exist_timeline_data,\
        amplitude2DAC,\
        bias_offset2DAC,\
        sample_period,\
        timeline_npts,\
        determine_bias_modulation,\
        timeline2adu,\
        plot_timeline,\
        plot_timeline_physical_layout,\
        model_timeline,\
        fit_timeline

    from .ASD import\
        read_ASD_picklefile,\
        plot_ASD,\
        plot_ASD_all,\
        plot_ASD_physical_layout,\
        make_ASD_tex_report

    from .oxford import\
        oxford_assign_temperature_labels,\
        oxford_assign_heater_ranges,\
        oxford_send_cmd,\
        oxford_init,\
        oxford_pidoff,\
        oxford_set_point,\
        oxford_read_set_point,\
        oxford_read_temperature,\
        oxford_read_bath_temperature,\
        oxford_read_all_temperatures,\
        oxford_check_calibration,\
        oxford_read_heater_level,\
        oxford_read_heater_range,\
        oxford_set_heater_range,\
        oxford_determine_best_heater_level,\
        oxford_increase_heater_range

    from .calibration_source import\
        calsource_init,\
        calsource_setFreqCommand,\
        calsource_outputFrequency,\
        calsource_setFrequency

    from .modulator import\
        init_hp33120a,\
        modulator_frequency,\
        modulator_read_frequency,\
        modulator_read_shape

    
    if with_pystudio:
        '''
        these methods connect to QubicStudio and require pystudio
        '''
        from .acquisition import\
            connect_QubicStudio,\
            verify_QS_connection,\
            configure_PID,\
            compute_offsets,\
            feedback_offsets,\
            get_amplitude,\
            get_mean,\
            integrate_scientific_data,\
            get_nsamples,\
            get_chunksize,\
            get_RawMask,\
            set_VoffsetTES,\
            get_iv_data,\
            get_iv_timeline,\
            get_ASD


        from .squids import\
            squid_test

    def __init__(self):
        self.assign_defaults()
        return

    def debugmsg(self,msg):
        if self.debuglevel>0:
            print('DEBUG %s : %s\n' % (dt.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),msg))
            if not self.logfile is None:
                self.writelog('DEBUG: %s' % msg)
            
        return
    
