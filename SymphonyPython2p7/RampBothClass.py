import numpy as np
from matplotlib import pyplot as plt
from AbstractProtocolClass import AbstractProtocol

class RampBoth( AbstractProtocol):
    '''Class for Ramp analysis'''

    def __init__( self, epoch_group_object, block_uuid, count):
        super( RampBoth, self).__init__( epoch_group_object, block_uuid, count)
        self.name = 'RampBoth'


    def load_data( self):
        '''Load data into array'''
        response_1 = np.zeros( shape = ( self['noPts'],))
        response_2 = np.zeros( shape = ( self['noPts'],))
        stimulus = self['holdingValue'] + \
            (self.time > self['preTime'])*(self.time < self['preTime'] \
            + self['stimTime']) * ( self['startAmp'] + \
            ( self['finalAmp'] - self['startAmp'])/self['stimTime'] \
            *( self.time - self['preTime']))


        # Length of response_2 seems broken, not sure why
        for epoch_no, epoch in enumerate( self.child_list):
            response_1 += epoch.fetch_response( 'Amp1')
            response_2 += epoch.fetch_response( 'Amp2')


        # Save back to class
        self.stimulus = stimulus
        self.response_1 = response_1/(epoch_no+1)
        self.response_2 = response_2/(epoch_no+1)


    def fetch_total_time( self):
        '''Returns maximum time of protocol'''
        return self['preTime'] + self['stimTime'] + self['tailTime']


    def plot_stimulus( self, ax):
        '''Plots responses based on stimulus ramps'''
        ax.plot( self.time, self.stimulus, lw=2, color='black')


    def plot_response( self, ax):
        '''Plots responses based on stimulus ramps'''
        ax.plot( self.time, self.response_1, lw=2, color='dodgerblue')
        ax.plot( self.time, self.response_2, lw=2, color='orange')


    def compute_whole_cell_conductance( self, start_voltage, stop_voltage):
        '''Computes whole cell conductance using linear part of ramp response'''
        ind = (self.stimulus > start_voltage) & (self.stimulus < stop_voltage)

        V_pts = self.stimulus[ind]
        I_pts = self.response[ind]

        X = np.array( [ np.ones( shape=( sum(ind),)), V_pts])

        self.condutance = ( np.linalg.lstsq( X, I_pts)[1], 'mS')

        return beta # Conductance

