import numpy as np
import scipy as sc
from matplotlib import pyplot as plt
from AbstractProtocolClass import AbstractProtocol

class StepRamp( AbstractProtocol):
    '''Class for StepRamp analysis'''

    def __init__( self, epoch_group_object, block_uuid, count):
        super( StepRamp, self).__init__( epoch_group_object, block_uuid, count)
        self.name = 'StepRamp'


    def load_data( self):
        '''Load data into array'''
        response = np.zeros( shape = ( self['noPts'],))
        stimulus = self['holdingValue'] \
            + (self.time > self['preTime'])*(self.time < self['preTime'] +
                    self['stepTime'] + self['rampTime'])*self['stepAmplitude'] \
            + (self.time > self['preTime'] + self['stepTime'])*(self.time < self['preTime'] \
            + self['stepTime'] + self['rampTime']) * self['rampAmplitude']/self['rampTime'] \
            *( self.time - self['preTime'] - self['stepTime'])


        for epoch_no, epoch in enumerate( self.child_list):
            response += epoch.fetch_response()


        # Save back to class
        self.stimulus = stimulus
        self.response = response/(epoch_no+1)


    def fetch_total_time( self):
        '''Returns maximum time of protocol'''
        return self['preTime'] + self['stepTime'] + self['rampTime'] + self['tailTime']


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


    def compute_input_resistance( self, data):
        '''Computes input resistance using initial step down'''
        base_ind = (self.time < self['preTime'])
        step_ind = (self.time > self['preTime'] + self['stepTime']/2.0) \
                *(self.time < self['preTime'] + self['stepTime'])

        base_resp = np.mean( self.response[base_ind])
        step_resp = np.mean( self.response[step_ind])

        self.input_resistance = 1e3*np.abs(
                self['stepAmplitude']/(step_resp-base_resp))

        data[0] = np.append( data[0], self.input_resistance)


    def compute_resting_potential( self, data, filter_response=False):
        '''Computes resting membrane potential by searching for zero crossing of
        current response'''

        ramp_ind = (self.time > self['preTime'] + self['stepTime']) \
                *(self.time < self['preTime'] + self['stepTime'] + \
                self['rampTime'])

        V_pts = self.stimulus[ramp_ind]
        I_pts = self.response[ramp_ind]

        # Filter the response
        if filter_response:
            I_pts = sc.signal.medfilt( I_pts, kernel_size=20)


        zero_ind = (I_pts[2:] > 0.0) & (I_pts[:-2] < 0.0)
        zero_ind = np.where( zero_ind)[0][0]

        self.RMP = V_pts[zero_ind]

        data[0] = np.append( data[0], self.RMP)
