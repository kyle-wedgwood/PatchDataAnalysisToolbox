import numpy as np
from AbstractProtocolClass import AbstractProtocol
from matplotlib import pyplot as plt

class PulseFamilyBoth( AbstractProtocol):
    '''Class for PulseFamilyBoth protocol analysis'''

    def __init__( self, epoch_group_object, block_uuid, count):
        super( PulseFamilyBoth, self).__init__( epoch_group_object, block_uuid, count)
        self.name = 'PulseFamilyBoth'


    def load_data( self):
        '''Loads data into array'''
        response_1 = np.zeros( shape=( self['noPts'], self['numberOfAverages']))
        response_2 = np.zeros( shape=( self['noPts'], self['numberOfAverages']))
        averaged_response_1 = np.zeros( shape=( self['noPts'], ))
        averaged_response_2 = np.zeros( shape=( self['noPts'], ))
        
        stimulus_1 = np.ones( shape=( self['noPts'],))*self['holdingValue']
        stimulus_2 = np.ones( shape=( self['noPts'],))*self['holdingValue']

        # Count how many completed runs there are
        no_completed_runs = len( self.child_list)
        include_flag = np.zeros( shape=( self['numberOfAverages']))
        include_flag[:no_completed_runs] = 1

        # Construct stimulus 1
        end_time = self['preTime1'] - self['intervalTime1'] + self['intervalTimeIncrement1']
        for i in range( self['numPulses1']):
            start_time = end_time + self['intervalTime1'] + (i-1)*self['intervalTimeInrement1']
            end_time = start_time + self['pulseTime1'] + i*self['pulseTimeIncrement1']
            ind = (start_time < self.time) & (self.time < end_time)
            stimulus_1[ind] = self['amplitude1'] + i*self['amplitudeIncrement1']


        # Construct stimulus 2
        end_time = self['preTime2'] - self['intervalTime2'] + self['intervalTimeIncrement2']
        for i in range( self['numPulses2']):
            start_time = end_time + self['intervalTime2'] + (i-1)*self['intervalTimeInrement2']
            end_time = start_time + self['pulseTime2'] + i*self['pulseTimeIncrement2']
            ind = (start_time < self.time) & (self.time < end_time)
            stimulus_2[ind] = self['amplitude2'] + i*self['amplitudeIncrement2']


        # Assuming epochs are time-ordered
        for epoch_no, epoch in enumerate( self.child_list):

            stim_pars = epoch.fetch_stimulus_pars()
            stim_amp  = stim_pars.get( 'amplitude')

            if include_flag[epoch_no]:
                response_1[:,epoch_no] = epoch.fetch_response( 'Amp1')
                response_2[:,epoch_no] = epoch.fetch_response( 'Amp2')
                averaged_response_1 += response_1[:,epoch_no]
                averaged_response_2 += response_2[:,epoch_no]


        # Compute averages
        averaged_response_1 /= no_completed_runs
        averaged_response_2 /= no_completed_runs

        # Save back to class
        self.stimulus_1 = stimulus_1
        self.stimulus_2 = stimulus_2
        self.response_1 = averaged_response_1
        self.response_2 = averaged_response_2


    def fetch_total_time( self):
        '''Returns maximum time of protocol'''
        total_time = self['preTime1'] + self['pulseTime1']
        for i in range(self['numPulses1']-1):
            total_time += self['intervalTime1'] + i*self['intervalTimeIncrement1']
            total_time += self['pulseTime1'] + (i+1)*self['pulseTimeIncrement1']

        return total_time


    def plot_stimulus( self, ax):
        '''Plots response based on stimulus pulses'''
        ax.plot( self.time, self.stimulus_1, lw=2, color='black')
        ax.plot( self.time, self.stimulus_2, lw=2, color='grey')


    def plot_response( self, ax):
        '''Plots response based on stimulus pulses'''
        ax.plot( self.time, self.response_1, lw=2, color='dodgerblue')
        ax.plot( self.time, self.response_2, lw=2, color='orange')

