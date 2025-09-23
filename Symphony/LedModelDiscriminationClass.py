import numpy as np
import h5py
from AbstractProtocolClass import AbstractProtocol
from matplotlib import pyplot as plt

class LedModelDiscrimination( AbstractProtocol):
    '''Class for LedModelDiscrimination protocol analysis'''

    def __init__(self, epoch_group_object, block_uuid, count):
        super(LedModelDiscrimination, self).__init__(epoch_group_object, block_uuid, count)
        self.name = 'LedModelDiscrimination'

        if not hasattr(self, 'wavelength'):
            self.wavelength = 470.0


    def load_data(self):
        '''Loads data into array'''

        if not hasattr(self, 'numberOfAverages'):
            self.numberOfAverages = 1

        # Count how many completed runs there are
        no_epochs = len(self.child_list)
        no_iterations = int(no_epochs/(self['numberOfAverages']))

        # This should be changed in the Matlab file
        self.numberOfAverages = int(self['numberOfAverages'])
        self.no_iterations = no_iterations

        # Create arrays for response and stimuli
        response = np.zeros(shape=(self['noPts'], no_iterations))
        stimulus = np.zeros(shape=(self['noPts'], no_iterations))
        model_a = np.zeros(shape=(self['noPts'], no_iterations))
        model_b = np.zeros(shape=(self['noPts'], no_iterations))
        rep_count = np.zeros(shape=(no_iterations))

        # Now establish which epochs to include based on rep count (assumes that
        # epochs are ordered)
        if no_iterations < 1:
            rep_count[:] = 1


        for epoch_no, epoch in enumerate(list(self.child_list)):

            stim_pars = epoch.fetch_stimulus_pars()
            stim_prop = epoch.fetch_stimulus_properties()

            pulse_type = stim_prop['type']
            iteration = int(stim_pars['iteration'])-1

            rep_count[iteration] += 1
            response[:,iteration] += epoch.fetch_response()
            stimulus[:,iteration] = epoch.fetch_light_stimulus('lightblue')

        # Load model outputs and average data
        for iteration in range(no_iterations):
            data = h5py.File('pb_0/iteration_%d.mat' % iteration)
            model_a[:,iteration] = data['/Ia']
            model_b[:,iteration] = data['/Ib']
            if np.all(response[:,iteration] == 0.0):
                response[:,iteration] = np.nan

            else:
                response[:,iteration] /= rep_count[iteration]


        # Save back to class
        self.stimulus = stimulus
        self.response = response
        self.model_a = model_a
        self.model_b = model_b


    def fetch_total_time(self):
        '''Returns maximum time of protocol'''
        return self['preTime'] + \
               self['stimTime'] + \
               self['tailTime']


    def plot_stimulus(self, ax, iteration=-1):
        '''Plots final control signal applied'''

        # New colorscheme
        color = self.wavelength_to_rgb(self["wavelength"])

        ax.plot(self.time, self.stimulus[:,iteration], lw=1.0, color=color)
        ax.set_ylabel('LED voltage (V)')


    def plot_response(self, ax, iteration=-1):
        '''Plots final recorded response based'''
        ax.plot(self.time, self.response[:,iteration], lw=0.1, \
                color='black', label='data')
        ax.plot(self.time, self.model_a[:,iteration], lw=0.1, \
                color='red', label='model a')
        ax.plot(self.time, self.model_b[:,iteration], lw=0.1, \
                color='blue', label='model b')
        ax.set_ylabel('Current (pA)')
        ax.legend()
