#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This file loads the data from the hdf5 file from Symphony into an array

Check if can get amplifier values directly for holding potential etc.

Created on Sun Feb 24 17:29:50 2019

@author: kcaw201
"""

from ExperimentClass import Experiment

filename = '2018-11-30.h5'
folder_name = filename.split( '.')[0]

exp_obj = Experiment( filename)
#exp_obj.plot_stimuli()
#exp_obj.plot_responses( named_pars=['Gfp present'], folder_name = 'dummy')
#exp_obj.make_plot( 'plotIVCurve', start_time=300, stop_time=500, named_pars=['Gfp present'], folder_name="dummy")

exp_obj.make_pdf_report()