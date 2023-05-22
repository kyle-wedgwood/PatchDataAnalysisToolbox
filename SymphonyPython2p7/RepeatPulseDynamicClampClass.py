import numpy as np
from AbstractProtocolClass import AbstractProtocol

class RepeatPulseDynamicClamp( AbstractProtocol):
    '''Class for RepeatPulseDynamicClamp analysis'''

    def __init__( self, epoch_group_object, block_uuid, count):
        super( RepeatPulseDynamicClamp, self).__init__( epoch_group_object, block_uuid, count)
        self.name = 'RepeatPulseDynamicClamp'

        # Load properties into class object
        properties_group = self.group.get( 'properties')
        if properties_group:
            properties = properties_group.attrs

            for prop_pair in properties.items():
                setattr( self, prop_pair[0], prop_pair[1])
                self.pdf_vars.update( { prop_pair[0]: prop_pair[1]})


    def load_data( self):
        '''Loads data into array'''
        response = np.zeros( shape=( self['noPts'], self['pulsesInFamily']))
        stimulus  = np.ones( shape=( self['noPts'], self['pulsesInFamily']))*self['holdingValue']
        dc_input = np.zeros( shape=( self['noPts'], self['pulsesInFamily']))

        for i in range( self['pulsesInFamily']):
            ind = (self.time > self['preTime'] + i*(self['interval']+self['pulseTime'])) \
                & (self.time < self['preTime'] + i*self['interval']+(i+1)*self['pulseTime'])
            stimulus[ind,i] += self['amplitude']


        epoch = self.child_list[0] # Only one epoch for this protocol
        self.stimulus = stimulus
        self.response = epoch.fetch_response()
        self.dc_input = epoch.fetch_dynamic_clamp_input( self['amp'])


    def fetch_total_time( self):
        '''Returns maximum time of protocol'''
        return self['preTime'] + self['pulsesInFamily']*self['pulseTime'] \
                + (self['pulsesInFamily']-1)*self['interval'] + self['tailTime']


    def plot_stimulus( self, ax):
        '''Plots response based on stimulus pulses'''
        ax.plot( self.time, self.stimulus, lw=1.0, color='black')
        ax.plot( self.time, self.dc_input, lw=1.0, color='firebrick')


    def plot_response( self, ax):
        '''Plots response based on stimulus pulses'''
        ax.plot( self.time, self.response, lw=1.0, color='black')


