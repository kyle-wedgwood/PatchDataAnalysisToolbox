#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Dec  9 13:23:29 2018

@author: kcaw201
"""

#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  4 21:44:34 2018

@author: kcaw201
"""

#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This file loads the data from the hdf5 file from Symphony into an array

Check if can get amplifier values directly for holding potential etc.

Created on Sat Dec  1 17:29:50 2018

@author: kcaw201
"""

import os
import h5py
import matplotlib.pyplot as plt
import numpy as np

def find_string( name, string):
    if string in name:
        return name


def create_dict( par_array):

    par_dict = {}

    for pair in par_array.items():
        par_dict[pair[0]] = pair[1]

    return par_dict


def check_attr( attr, par_array):

    if attr in par_array.keys():
        return par_array.get( attr)
    else:
        return ''


filename = '2018-11-30.h5'
folder_name = filename.split( '.')[0]

if not os.path.exists( folder_name):
    os.makedirs( folder_name)

file_id = h5py.File( filename, 'r')

exp_uuid = file_id.items()[-1][0]
exp_group = file_id.get( exp_uuid)

uuid = exp_group.get( 'sources').keys()[0]
subject_group = exp_group.get( 'sources/' + uuid)

prep_list = subject_group.get( 'sources/').keys()

cell_data = []

overall_cell_no = 0

for prep_no, prep_uuid in enumerate( prep_list):

    prep_group = subject_group.get( 'sources/' + prep_uuid)
    cell_list = prep_group.get( 'sources/').keys()

    prep_pars = prep_group.get( 'properties').attrs
    holding_potential = check_attr( 'Holding potential', prep_pars)
    holding_potential = -60.0
    coating  = check_attr( 'Coating', prep_pars)
    category = check_attr( 'Category', prep_pars)

    plot_pars = { 'coating': coating,
                  'category': category}

    for cell_no, cell_uuid in enumerate( cell_list):

    #    peak_current = np.zeros( shape=(11,3))

        cell_group = prep_group.get( 'sources/' + cell_uuid)
        cell_pars = cell_group.get( 'properties').attrs

        gfp_present = check_attr( 'Gfp present', cell_pars)
        plot_pars['gfp'] = gfp_present

        uuid = cell_group.get( 'epochGroups').keys()[0]
        blocks_group = cell_group.get( 'epochGroups/' + uuid + '/epochBlocks')

        for block_no, block_uuid in enumerate( list( blocks_group)):

            block_group = blocks_group.get( block_uuid)

            protocol_pars = block_group.get( 'protocolParameters').attrs
#            protocol_pars = {}

#            for pair in protocol_pars.items():
#                protocol_pars[pair[0]] = pair[1]

            # Protocol parameters - look to change this to dict
            no_ave   = protocol_pars.get( 'numberOfAverages')
            no_pulse = protocol_pars.get( 'pulsesInFamily')
            sample_rate = protocol_pars.get( 'sampleRate')
            increment = protocol_pars.get( 'incrementPerPulse')
            first_pulse = protocol_pars.get( 'firstPulseSignal')
            pre_time = protocol_pars.get( 'preTime')
            stim_time = protocol_pars.get( 'stimTime')
            tail_time = protocol_pars.get( 'tailTime')

            cmap = np.linspace( 1, 0, no_pulse+1)
            cmap = cmap[1:]
            cmap = np.tile( cmap, (3,1))

            total_time = pre_time + stim_time + tail_time

            no_pts = int( total_time*sample_rate/1000.0)

            time = np.array( range( no_pts))/sample_rate*1000.0 # time in ms
            voltage_ref = np.array( range( no_pulse))*increment + first_pulse + holding_potential
            mean_current = np.zeros( shape=( no_pts, no_pulse))

            current = np.zeros( shape=( no_pulse, no_ave))
            voltage = np.zeros( shape=( no_pulse, no_ave))
            rep_count = np.zeros( shape=( no_pulse,))

            epoch_list = block_group.get( 'epochs')

            for epoch_no, epoch_uuid in enumerate( list( epoch_list)):

                response_group = epoch_list.get( epoch_uuid + '/responses')
                stimulus_group = epoch_list.get( epoch_uuid + '/stimuli')

                uuid = response_group.visit( lambda name: find_string( name, 'data'))
                response_data = response_group.get( uuid)

                uuid = stimulus_group.visit( lambda name: find_string( name, 'Amp'))
                cell_pars = stimulus_group.get( uuid + '/parameters')
                stim_amp  = cell_pars.attrs.get( 'amplitude')

                I = [ val[0] for val in response_data ]

                i = np.argmin( (voltage_ref - stim_amp - holding_potential)**2)
                k = int( rep_count[i])
                rep_count[i] += 1

                mean_current[:,i] += np.array(I)/3.0
    #        base_current = np.mean( I[0:499])
                base_current = 0.0
                current[i,k] = np.mean( I[3000:5000]) - base_current
                voltage[i,k] = stim_amp + holding_potential
    #        peak_current = np.max( I[550:1000] - base_current)
                print( 'Done epoch %d of block %d of cell %d' % (epoch_no,block_no,overall_cell_no))


            # Make a plot of current
            plt.rcParams.update({'font.size': 22})
            fig, ax = plt.subplots( figsize=(12,8))
            ax.set_xlabel( 'Time (ms)')
            ax.set_ylabel( 'I (pA)')
            for i in range( no_pulse):
                ax.plot( time, mean_current[:,i], lw=0.1, color=cmap[:,i])

            xlim = ax.get_xlim()
            ylim = ax.get_ylim()

#            if gfp_flag:
#                ax.text( 0.75*xlim[1], ylim[0]+0.1*(ylim[1]-ylim[0]), 'GFP present')

            string = ''
            values = ()
            for key, val in plot_pars.items():
                string += key + ': %s, '
                values = values + (val,)

            string = string[:-2]
            ax.set_title( string % values)

            fig_filename = '%s/cell_%d_block_%d_voltage_clamp' % (folder_name,overall_cell_no,block_no)
            fig.savefig( fig_filename, bbox_inches='tight')

            cell_data.append( (np.mean( current, axis=1), voltage))

            fig2, ax2 = plt.subplots( figsize=(12,8))
            ax2.set_xlabel( 'Voltage (mV)')
            ax2.set_ylabel( 'I (pA)')
            ax2.plot( voltage, np.mean( current, axis=1), color='black', lw=4)

            xlim = ax2.get_xlim()
            ylim = ax2.get_ylim()

            ax2.set_title( string % values)

#            if gfp_flag:
#                ax2.text( 0.75*xlim[1], ylim[0]+0.1*(ylim[1]-ylim[0]), 'GFP present')

            ax2.set_title( 'Coating: %s, Category: %s' % (coating,category))

            fig_filename = '%s/cell_%d_block_%d_IV_curve' % (folder_name,overall_cell_no,block_no)
            fig2.savefig( fig_filename, bbox_inches='tight')


        overall_cell_no += 1
