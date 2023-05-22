import numpy as np
from AbstractProtocolClass import AbstractProtocol
from matplotlib import pyplot as plt

class PulseFamilyDynamicClamp( AbstractProtocol):
    '''Class for PulseFamilyDynamicClamp analysis'''

    def __init__( self, epoch_group_object, block_uuid, count):
        super( PulseFamilyDynamicClamp, self).__init__( epoch_group_object, block_uuid, count)
        self.name = 'PulseFamilyDynamicClamp'

        # Load properties into class object
        properties_group = self.group.get( 'properties')
        if properties_group:
            properties = properties_group.attrs

            for prop_pair in properties.items():
                setattr( self, prop_pair[0], prop_pair[1])
                self.pdf_vars.update( { prop_pair[0]: prop_pair[1]})


    def load_data( self):
        '''Loads data into array'''
        stimulus_ref = np.array( range( \
            self['pulsesInFamily']))*self['incrementPerPulse'] + \
            self['firstPulseSignal']

        response = np.zeros( shape=( self['noPts'], self['pulsesInFamily']))
        stimulus = np.ones( shape=( self['noPts'], self['pulsesInFamily']))*self['holdingValue']
        dc_input  = np.zeros( shape=( self['noPts'], self['pulsesInFamily']))

        ind = (self.time > self['preTime']) & (self.time < self['preTime'] + self['stimTime'])

        for i in range( self['pulsesInFamily']):
            stimulus[ind,i] += stimulus_ref[i]


        # Count how many completed runs there are
        no_epochs = len( self.child_list)

        pulseGroup = -1 # For use in case stimulus is not changing in amplitude

        for epoch_no, epoch in enumerate( self.child_list):

            stim_pars = epoch.fetch_stimulus_pars()
            stim_amp  = stim_pars.get( 'amplitude')

            if self['incrementPerPulse'] == 0:
                pulseGroup += 1
            else:
                pulseFamily = np.argmin( (stimulus_ref - stim_amp)**2)
                pulseGroup = pulseFamily


            response[:,pulseGroup] = epoch.fetch_response()
            dc_input[:,pulseGroup]  = epoch.fetch_dynamic_clamp_input( self['amp'])


        # Save back to class
        self.stimulus = stimulus
        self.dc_input = dc_input
        self.response = response


    def fetch_total_time( self):
        '''Returns maximum time of protocol'''
        return self['preTime'] + self['stimTime'] + self['tailTime']


    def plot_stimulus( self, ax):
        '''Plots response based on stimulus pulses'''
        cmap = np.linspace( 1, 0, self['pulsesInFamily']+1)
        cmap = cmap[1:]
        cmap = np.tile( cmap, (3,1))

        for i in range( self['pulsesInFamily']):
            ax.plot( self.time, self.stimulus[:,i], lw=1.0, color=cmap[:,i])
            ax.plot( self.time, self.dc_input[:,i], lw=1.0, color='firebrick')


    def plot_response( self, ax):
        '''Plots response based on stimulus pulses'''
        cmap = np.linspace( 1, 0, self['pulsesInFamily']+1)
        cmap = cmap[1:]
        cmap = np.tile( cmap, (3,1))

        for i in range( self['pulsesInFamily']):
            ax.plot( self.time, self.response[:,i], lw=0.1, color=cmap[:,i])


