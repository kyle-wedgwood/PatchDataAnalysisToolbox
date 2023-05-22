import numpy as np
from matplotlib import pyplot as plt
from AbstractProtocolClass import AbstractProtocol

class GapFree( AbstractProtocol):
    '''Class for GapFreeClass analysis'''

    def __init__( self, epoch_group_object, block_uuid, count):
        super( GapFree, self).__init__( epoch_group_object, block_uuid, count)
        self.name = 'GapFree'


    def load_data( self):
        '''Load data into array'''
        response = np.zeros( 0)

        # Might need to concatenate here
        for epoch_no, epoch in enumerate( self.child_list):
            temp_response = epoch.fetch_response()
            response = np.append( response, temp_response)


        # Save back to class
        self.response = response

        # Overtime time as necessary
        noPts = len( self.response)
        self.time = np.array( range( noPts))/self['sampleRate']*1000.0


    def fetch_total_time( self):
        '''Returns maximum time of protocol'''
        if 'numberOfAverages' in self.__dict__.keys():
            numberOfAverages = self['numberOfAverages']
        else:
            numberOfAverages = 1


        return self['updateTime']*numberOfAverages


    def plot_stimulus( self, ax):
        '''Required to overload base class function'''
        pass


    def plot_response( self, ax):
        '''Plots response'''
        ax.plot( self.time, self.response, lw=2, color='black')


    def plot_stimuli_and_responses( self, protocol='all', named_pars=[], folder_name=None):
        '''Sets up figure and axis handle then calls plotting function'''
        if (protocol == 'all' or protocol == self.name):
            if self.operating_mode == 'VClamp':
                r_label = 'I (pA)'
            elif (self.operating_mode == 'IClamp') \
                    or (self.operating_mode == 'I0'):
                r_label = 'V (mV)'


            # Now find plot parameters
            plot_pars = {}
            plot_pars = self.fetch_plot_pars( plot_pars, named_pars)

            plt.rcParams.update({'font.size': 22})
            fig, ax = plt.subplots( figsize=(24,8))
            ax.set_xlabel( 'Time (ms)')
            ax.set_ylabel( r_label)

            self.plot_response( ax)

            fig_filename = self.post_process_figure( fig, ax, plot_pars, \
                 folder_name, 'stimulus_response')

            return fig_filename
