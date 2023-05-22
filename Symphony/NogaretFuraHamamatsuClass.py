import os
import sys
import numpy as np
from os.path import exists
from AbstractProtocolClass import AbstractProtocol
from matplotlib import pyplot as plt

class NogaretFuraHamamatsu(AbstractProtocol):
    '''Class for NogaretFuraHamamatsu analysis'''

    def __init__( self, epoch_group_object, block_uuid, count):
        self.imaging_data_available = False
        self.folderName = 'run1'
        self.exclude_list = [ 'imaging_time', 'imaging_response', 'imaging_data_available']

        super( NogaretFuraHamamatsu, self).__init__( epoch_group_object, block_uuid, count)
        self.name = 'NogaretFuraHamamatsu'

        # Load properties into class object - NEED TO FIX THIS
        properties_group = self.group.get( 'properties')
        if properties_group:
            properties = properties_group.attrs

            for prop_pair in properties.items():
                setattr( self, prop_pair[0], prop_pair[1])
                self.pdf_vars.update( { prop_pair[0]: prop_pair[1]})


    def load_data( self):
        '''Loads data into array'''

        if len( self.child_list) == 1:
            epoch = self.child_list[0]
            self.response = epoch.fetch_response()
            self.stimulus = epoch.fetch_stimulus()

        self.folderName = 'run1'
        fluo_data_filename = self['folderName'] + '_signals.dat'

        # Search for file in directories
        for dirname, dirs, files in os.walk('.'):
            for filename in files:
                if self.imaging_data_available == True:
                    break

                if filename == fluo_data_filename:
                    fluo_data_filename = dirname + '/' + filename
                    self.imaging_data_available = True
                    break


        if self.imaging_data_available == True:
            no_frames = int(len(self.stimulus)/self['sampleRate']/self['interval']) + 1
            self.imaging_time = np.array(range(no_frames))*self['interval']
            self.imaging_response = np.loadtxt(fluo_data_filename)
            

        # Update time
        self.noPts = len(self.response)
        self.totalTime = self['noPts']/self['sampleRate']
        self.time = np.array( range( self['noPts']))/self['sampleRate'] # time in s


    def load_imaging_data( self):
        '''Tries to find and load imaging data'''


    def fetch_total_time( self):
        '''Returns maximum time of protocol'''
        return 1.0 # Return dummy value - will be updated in load_data()


    def plot_stimulus( self, ax):
        '''Plots response based on stimulus pulses'''
        ax.plot( self.time, self.stimulus, lw=1.0, color='black')


    def plot_response( self, ax):
        '''Plots response based on stimulus pulses'''
        ax.plot( self.time, self.response, lw=0.1, color='black')


    def plot_imaging_response( self, ax):
        '''Plots response based on stimulus pulses'''
        ax.plot( self.imaging_time, self.imaging_response, lw=1.0, color='red')
        y_max = np.max([1,1.1*np.nanmax(self.imaging_response)])
        ax.set_ylim([0,y_max])


    def plot_stimuli_and_responses( self, protocol='all', named_pars=[], folder_name=None):
        '''Sets up figure and axis handle then calls plotting function'''

        # Now find plot parameters
        plot_pars = {}
        plot_pars = self.fetch_plot_pars( plot_pars, named_pars)

        plt.rcParams.update({'font.size': 22})
        fig, (ax_S,ax_R) = plt.subplots( nrows=2, figsize=(24,8))
        ax_S.set_ylabel( 'I (pA)')
        ax_R.set_xlabel( 'Time (s)')
        ax_R.set_ylabel( 'V (mV)')

        self.plot_stimulus( ax_S)
        self.plot_response( ax_R)
        
        if self.imaging_data_available:
            ax_I = ax_R.twinx()
            ax_I.set_ylabel( '340:380', color='red')
            self.plot_imaging_response( ax_I)


        fig_filename = self.post_process_figure( fig, ax_R, plot_pars, \
             folder_name, 'stimulus_response')

        return fig_filename
