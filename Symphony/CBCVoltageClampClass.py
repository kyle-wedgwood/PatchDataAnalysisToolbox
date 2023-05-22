import numpy as np
from matplotlib import pyplot as plt
from AbstractProtocolClass import AbstractProtocol

class CBCVoltageClamp( AbstractProtocol):
    '''Class for CBCVoltageClamp analysis'''

    def __init__(self, epoch_group_object, block_uuid, count):
        super(CBCVoltageClamp, self).__init__(epoch_group_object, block_uuid, count)
        self.name = 'CBCVoltageClamp'


    def load_data(self):
        '''Load data into array'''
        response = np.zeros(0)
        stimulus = np.zeros(0)

        for epoch_no, epoch in enumerate(self.child_list):
            stim_pars = epoch.fetch_stimulus_pars()
            stim_prop = epoch.fetch_stimulus_properties()

            if stim_prop.get('state') == 2:
                temp_response = epoch.fetch_response()
                stimulus = np.append(stimulus, stim_pars['bifCurrent'])
                response = np.append(response, np.mean(temp_response))


        # Save back to class
        self.response = response
        self.stimulus = stimulus


    def fetch_total_time(self):
        '''Returns maximum time of protocol'''
        return 1000.0


    def plot_stimulus( self, ax):
        '''Required to overload base class function'''
        pass


    def plot_response( self, ax):
        '''Required to overload base class function'''
        pass


    def plot_stimuli_and_responses( self, protocol='all', named_pars=[], folder_name=None):
        '''Sets up figure and axis handle then calls plotting function'''
        if (protocol == 'all' or protocol == self.name):

            # Now find plot parameters
            plot_pars = {}
            plot_pars = self.fetch_plot_pars(plot_pars, named_pars)

            plt.rcParams.update({'font.size': 22})
            fig, ax = plt.subplots( figsize=(24,12))
            ax.set_xlabel('Current (pA)')
            ax.set_ylabel('Voltage (mV)')

            ax.plot(self.stimulus, self.response, linestyle='None', \
                    marker='.', markersize=40)

            fig_filename = self.post_process_figure(fig, ax, plot_pars, \
                 folder_name, 'stimulus_response')

            return fig_filename


    def save_data_ascii( self, folder_name='.'):
        '''Saves stimulus and response to a text file'''
        cell_no = self.find_cell_no()
        prep_no = self.find_prep_no()

        filename = \
        '%s/prep_%d_cell_%d_group_%d_block_%d_%s_time_stimulus_response.dat' % \
        (folder_name, prep_no, cell_no, \
                self.parent.no, self.no, self.__class__.__name__)

        buf = np.nan*np.ones( shape=( self.stimulus.shape[0]))
        data = np.stack( (self.stimulus, buf, self.response), axis=1)

        np.savetxt( filename, data)