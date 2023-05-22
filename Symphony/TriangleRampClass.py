import numpy as np
from matplotlib import pyplot as plt
from AbstractProtocolClass import AbstractProtocol

class TriangleRamp(AbstractProtocol):
    '''Class for TriangleRamp analysis'''

    def __init__(self, epoch_group_object, block_uuid, count):
        super(TriangleRamp, self).__init__(epoch_group_object, block_uuid, count)
        self.name = 'TriangleRamp'


    def load_data(self):
        '''Load data into array'''
        response = np.zeros(shape = (self['noPts'],))

        amplitude = self['finalAmp'] - self['startAmp']

        up_ramp = (self.time > self['preTime'])*(self.time < self['preTime'] \
            + self['stimTime']) * amplitude/self['stimTime'] \
            *(self.time - self['preTime'])

        down_ramp = (self.time >= self['preTime'] + self['stimTime']) \
            *(self.time < self['preTime'] + 2.0*self['stimTime']) \
            *(amplitude-amplitude/self['stimTime']*(self.time-self['preTime']-self['stimTime']))
          
        stimulus = self['holdingValue'] + self['startAmp'] + up_ramp + down_ramp

        for epoch_no, epoch in enumerate(self.child_list):
            n = len(response)
            epoch_data = epoch.fetch_response()[:n]
            response += epoch_data


        # Save back to class
        self.stimulus = stimulus
        self.response = response/(epoch_no+1)


    def fetch_total_time( self):
        '''Returns maximum time of protocol'''
        return self['preTime'] + 2.0*self['stimTime'] + self['tailTime']


    def plot_stimulus( self, ax):
        '''Plots responses based on stimulus ramps'''
        ax.plot(self.time, self.stimulus, lw=2, color='black')


    def plot_response( self, ax):
        '''Plots responses based on stimulus ramps'''
        ax.plot(self.time, self.response, lw=2, color='black')

