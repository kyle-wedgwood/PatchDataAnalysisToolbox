import numpy as np
from AbstractProtocolClass import AbstractProtocol
from matplotlib import pyplot as plt

class BlueGeneralStim( AbstractProtocol):
    '''Class for BlueGeneralStim analysis'''

    def __init__( self, epoch_group_object, block_uuid, count):
        super( BlueGeneralStim, self).__init__( epoch_group_object, block_uuid, count)
        self.name = 'BlueGeneralStim'

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
            self.stimulus = epoch.fetch_light_stimulus('light340')

            # Update time
            self.noPts = len(self.response)
            self.totalTime = self['noPts']/self['sampleRate']
            self.time = np.array( range( self['noPts']))/self['sampleRate'] # time in s

        else:
            self.noPts = 0
            self.totalTime = 0.0
            self.time = []
            self.response = []
            self.stimulus = []


    def fetch_total_time( self):
        '''Returns maximum time of protocol'''
        return 1.0 # Return dummy value - will be updated in load_data()


    def plot_stimulus( self, ax):
        '''Plots response based on stimulus pulses'''
        ax.plot( self.time, self.stimulus, lw=1.0, color='black')


    def plot_response( self, ax):
        '''Plots response based on stimulus pulses'''
        ax.plot( self.time, self.response, lw=0.1, color='black')


    def plot_stimuli_and_responses( self, protocol='all', named_pars=[], folder_name=None):
        '''Sets up figure and axis handle then calls plotting function'''

        # Now find plot parameters
        plot_pars = {}
        plot_pars = self.fetch_plot_pars( plot_pars, named_pars)

        plt.rcParams.update({'font.size': 22})
        fig, (ax_S,ax_R) = plt.subplots( nrows=2, figsize=(24,8))

        ax_S.set_ylabel( 'LED voltage (V)')
        ax_R.set_xlabel( 'Time (s)')
        
        if self.operating_mode == 'VClamp':
            ax_R.set_ylabel( 'I (pA)')

        elif self.operating_mode == 'IClamp':
            ax_R.set_ylabel( 'V (mV)')


        self.plot_stimulus( ax_S)
        self.plot_response( ax_R)

        fig_filename = self.post_process_figure( fig, ax_R, plot_pars, \
             folder_name, 'stimulus_response')

        return fig_filename
