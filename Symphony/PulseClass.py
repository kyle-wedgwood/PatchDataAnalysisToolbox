import numpy as np
from AbstractProtocolClass import AbstractProtocol
from matplotlib import pyplot as plt

class Pulse( AbstractProtocol):
    '''Class for Pulse analysis'''

    def __init__( self, epoch_group_object, block_uuid, count):
        super( Pulse, self).__init__( epoch_group_object, block_uuid, count)
        self.name = 'Pulse'

        # Load properties into class object - NEED TO FIX THIS
        properties_group = self.group.get( 'properties')
        if properties_group:
            properties = properties_group.attrs

            for prop_pair in properties.items():
                setattr( self, prop_pair[0], prop_pair[1])
                self.pdf_vars.update( { prop_pair[0]: prop_pair[1]})


    def load_data( self):
        '''Loads data into array'''
        response = np.zeros( shape=( self['noPts']))
        stimulus = np.ones( shape=( self['noPts']))*self['holdingValue']

        rep_count = 0

        ind = (self.time > self['preTime']) & (self.time < self['preTime'] + self['stimTime'])
        stimulus[ind] += self['pulseAmplitude']

        for epoch in  self.child_list:

            response += epoch.fetch_response()
            rep_count += 1


        response /= rep_count

        # Save back to class
        self.stimulus = stimulus
        self.response = response


    def fetch_total_time( self):
        '''Returns maximum time of protocol'''
        return self['preTime'] + self['stimTime'] + self['tailTime']


    def plot_stimulus( self, ax):
        '''Plots response based on stimulus pulses'''
        ax.plot( self.time, self.stimulus, lw=1.0, color='black')


    def plot_response( self, ax):
        '''Plots response based on stimulus pulses'''
        ax.plot( self.time, self.response, lw=0.1, color='black')

