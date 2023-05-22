import numpy as np
from matplotlib import pyplot as plt
from AbstractProtocolClass import AbstractProtocol
from scipy.signal import find_peaks

class OrnsteinUhlenbeck( AbstractProtocol):
    '''Class for OrnsteinUhlenbeck analysis'''

    def __init__( self, epoch_group_object, block_uuid, count):
        super( OrnsteinUhlenbeck, self).__init__( epoch_group_object, block_uuid, count)
        self.name = 'GapFreeRecord'


    def load_data( self):
        '''Load data into array'''

        # Might need to concatenate here
        if len( self.child_list) == 1:
            epoch = self.child_list[0]
            self.response = epoch.fetch_response()
            self.stimulus = epoch.fetch_stimulus()


        # Overtime time as necessary
        noPts = len( self.response)
        self.time = np.array( range( noPts))/self['sampleRate']


    def fetch_total_time( self):
        '''Returns maximum time of protocol'''
        return self['recordTime']


    def plot_stimulus( self, ax):
        '''Required to overload base class function'''
        ax.plot( self.time, self.stimulus, lw=0.5, color='black')


    def plot_response( self, ax):
        '''Plots response'''
        ax.plot( self.time, self.response, lw=0.5, color='black')


    def plot_stimuli_and_responses( self, protocol='all', named_pars=[], folder_name=None):
        '''Sets up figure and axis handle then calls plotting function'''

        # Now find plot parameters
        plot_pars = {}
        plot_pars = self.fetch_plot_pars( plot_pars, named_pars)

        plt.rcParams.update({'font.size': 22})
        fig, (ax_S,ax_R) = plt.subplots( nrows=2, figsize=(24,8))
        ax_S.set_xlabel( 'Time (s)')
        ax_S.set_ylabel( 'I (pA)')
        ax_R.set_xlabel( 'Time (s)')
        ax_R.set_ylabel( 'V (mV)')

        self.plot_stimulus( ax_S)
        self.plot_response( ax_R)

        fig_filename = self.post_process_figure( fig, ax_R, plot_pars, \
             folder_name, 'stimulus_response')

        return fig_filename


    def plot_ISI_histogram( self, noBins=20, named_pars=None, folder_name=None):
        '''Find spikes times and plot histogram of period'''

        peak_ind = find_peaks( self.response, height=-10, distance=1000,
                prominence=20)[0]
        spike_times = self.time[peak_ind]
        ISIs = np.diff( spike_times)

        fig, ax = plt.subplots( figsize=(12,8))

        plot_pars = {}
        #plot_pars = self.fetch_plot_pars( plot_pars, named_pars)

        ax.set_xlabel( 'ISI (s)')
        ax.set_ylabel( 'Freq.')
        count, bins = np.histogram( ISIs, bins=noBins)

        ax.plot( (bins[1:]+bins[:-1])/2.0, count)

        mean = np.mean( ISIs)
        std = np.std( ISIs)

        ax.set_title( 'Total: %d, Mean: %0.2f, Std: %0.2f' % (len( ISIs),mean,std))

        if folder_name: self.save_fig( fig, folder_name, 'ISI_histogram')


