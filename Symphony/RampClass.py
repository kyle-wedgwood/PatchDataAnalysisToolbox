import numpy as np
from matplotlib import pyplot as plt
from AbstractProtocolClass import AbstractProtocol

class Ramp( AbstractProtocol):
    '''Class for Ramp analysis'''

    def __init__( self, epoch_group_object, block_uuid, count):
        super( Ramp, self).__init__( epoch_group_object, block_uuid, count)
        self.name = 'Ramp'


    def load_data( self):
        '''Load data into array'''
        # HACK TO DEAL WITH CHANGE TO RAMP PARAMETRISATION ##
        if not hasattr(self, 'startAmp'):
            self.startAmp = 0.0
            self.finalAmp = self['rampAmplitude']
            
            
        response = np.zeros( shape = ( self['noPts'],))
        stimulus = self['holdingValue'] \
            + (self.time <= self['preTime'])*self['startAmp'] \
            + (self.time > self['preTime'])*(self.time < self['preTime'] \
            + self['stimTime']) * ( self['startAmp'] \
            + ( self['finalAmp'] - self['startAmp'])/self['stimTime'] \
            *( self.time - self['preTime']))


        for epoch_no, epoch in enumerate( self.child_list):
            response += epoch.fetch_response()


        # Save back to class
        self.stimulus = stimulus
        self.response = response/(epoch_no+1)


    def fetch_total_time( self):
        '''Returns maximum time of protocol'''
        return self['preTime'] + self['stimTime'] + self['tailTime']


    def plot_stimulus( self, ax):
        '''Plots responses based on stimulus ramps'''
        ax.plot( self.time, self.stimulus, lw=2, color='black')


    def plot_response( self, ax):
        '''Plots responses based on stimulus ramps'''
        ax.plot( self.time, self.response, lw=2, color='black')


    def compute_whole_cell_conductance( self, data, start_voltage, stop_voltage):
        '''Computes whole cell conductance using linear part of ramp response'''
        ind = (self.stimulus > start_voltage) & (self.stimulus < stop_voltage)

        V_pts = self.stimulus[ind]
        I_pts = self.response[ind]/self.membrane_capacitance

        X = np.array( [ np.ones( shape=( sum(ind),)), V_pts])

        self.conductance = np.linalg.lstsq( X.transpose(), I_pts)[0][1]

        data[0] = np.append( data[0], self.conductance)

