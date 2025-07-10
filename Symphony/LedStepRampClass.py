import numpy as np
import scipy as sc
from matplotlib import pyplot as plt
from AbstractProtocolClass import AbstractProtocol

class LedStepRamp( AbstractProtocol):
    '''Class for LedStepRamp analysis'''

    def __init__(self, epoch_group_object, block_uuid, count):
        super(LedStepRamp, self).__init__( epoch_group_object, block_uuid, count)
        self.name = 'LedStepRamp'


    def load_data( self):
        '''Load data into array'''
        response = np.zeros( shape = ( self['noPts'],))
        stimulus =  (self.time > self['preTime'])*(self.time < self['preTime'] +
                    self['stepTime'] + self['rampTime'])*self['stepAmplitude'] \
            + (self.time > self['preTime'] + self['stepTime'])*(self.time < self['preTime'] \
            + self['stepTime'] + self['rampTime']) * self['rampAmplitude']/self['rampTime'] \
            *(self.time - self['preTime'] - self['stepTime'])


        for epoch_no, epoch in enumerate(self.child_list):
            response += epoch.fetch_response()


        # Save back to class
        self.stimulus = stimulus
        self.response = response/(epoch_no+1)


    def fetch_total_time( self):
        '''Returns maximum time of protocol'''
        return self['preTime'] + self['stepTime'] + self['rampTime'] + self['tailTime']


    def plot_stimulus( self, ax):
        '''Plots responses based on stimulus ramps'''
        color = self.wavelength_to_rgb(self["wavelength"])
        ax.plot( self.time, self.stimulus, lw=2, color=color)
        ax.set_ylabel('LED voltage (V)')


    def plot_response( self, ax):
        '''Plots responses based on stimulus ramps'''
        ax.plot( self.time, self.response, lw=2, color='black')

