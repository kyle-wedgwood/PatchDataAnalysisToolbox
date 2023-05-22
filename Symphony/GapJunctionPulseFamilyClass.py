import numpy as np
from AbstractProtocolClass import AbstractProtocol
from matplotlib import pyplot as plt

class GapJunctionPulseFamily( AbstractProtocol):
    '''Class for GapJunctionPulseFamily analysis'''

    def __init__( self, epoch_group_object, block_uuid, count):
        super( GapJunctionPulseFamily, self).__init__( epoch_group_object, block_uuid, count)
        self.name = 'GapJunctionPulseFamily'

        # Putting colormap options here
        self.cmap_1 = self.create_color_map( 'Blues', self['pulsesInFamily']+1)
        self.cmap_2 = self.create_color_map( 'Oranges', self['pulsesInFamily']+1)

        # Find membrane capacitance of second cell
        self.amp_alt_prop = self.fetch_amplifier_properties( amp=2)[0]
        if 'Amp1' in self.amp_name:
            self.membrane_capacitance_1 = self.membrane_capacitance
            self.membrane_capacitance_2 = self.amp_alt_prop['membraneCapacitance']*1e12
        elif 'Amp2' in self.amp_name:
            self.membrane_capacitance_1 = self.amp_alt_prop['membraneCapacitance']*1e12
            self.membrane_capacitance_2 = self.membrane_capacitance


    def load_data( self):
        '''Loads data into array'''
        stimulus_ref = np.array( range( \
            self['pulsesInFamily']))*self['incrementPerPulse'] + \
            self['firstPulseSignal']

        response_1 = np.zeros( shape=( self['noPts'], self['pulsesInFamily']*self['numberOfAverages']))
        response_2 = np.zeros( shape=( self['noPts'], self['pulsesInFamily']*self['numberOfAverages']))
        average_response_1 = np.zeros( shape=( self['noPts'], self['pulsesInFamily']))
        average_response_2 = np.zeros( shape=( self['noPts'], self['pulsesInFamily']))
        stimulus_1 = np.zeros( shape=( self['noPts'], self['pulsesInFamily']))
        stimulus_2 = np.zeros( shape=( self['noPts'], self['pulsesInFamily']))

        pre_ind  = (self.time < self['preTime'])
        stim_1_ind = (self.time > self['preTime']) & (self.time < self['preTime'] + self['stimTime'])
        pulse_2_start = self['preTime'] + self['stimTime'] \
            + self['intervalTime']
        pulse_2_end = pulse_2_start + self['stimTime']
        stim_2_ind = (self.time > pulse_2_start) & (self.time < pulse_2_end)

        include_flag = np.zeros( shape=( self['pulsesInFamily']*self['numberOfAverages']))
        response_flag = np.zeros( shape=( self['pulsesInFamily']*self['numberOfAverages']))
        rep_count = np.zeros( shape=( self['pulsesInFamily']))

        # Set stimulus
        for i in range( self['pulsesInFamily']):
            stimulus_1[stim_1_ind,i] = self['firstPulseSignal'] + i*self['incrementPerPulse']
            stimulus_2[stim_2_ind,i] = self['firstPulseSignal'] + i*self['incrementPerPulse']


        stimulus_1 += self['holdingValue']
        stimulus_2 += self['holdingValue']

        # Count how many completed runs there are
        no_epochs = len( self.child_list)
        no_completed_runs = int( no_epochs/self['pulsesInFamily'])

        # Now establish which epochs to include based on rep count (assumes that
        # epochs are ordered)
        if no_completed_runs < 1:
            include_flag[:self['pulsesInFamily']] = 1
            rep_count[:] = 1
        else:
            include_flag[:no_completed_runs*self['pulsesInFamily']] = 1
            rep_count[:] = no_completed_runs


        # Now load responses
        for epoch_no, epoch in enumerate( self.child_list):

            stim_pars = epoch.fetch_stimulus_pars()
            stim_prop = epoch.fetch_stimulus_properties()
            stim_amp  = stim_pars.get( 'amplitude')

            pulseFamily = np.argmin( (stimulus_ref - stim_amp)**2)
            pulseGroup = pulseFamily

            while response_flag[pulseGroup] == 1:
                pulseGroup += self['pulsesInFamily']

            if include_flag[pulseGroup]:
                response_1[:,pulseGroup] += epoch.fetch_response( 'Amp1')
                response_2[:,pulseGroup] += epoch.fetch_response( 'Amp2')
                response_flag[pulseGroup] = 1


            rep_count[pulseFamily] += 1


        for pulseGroup in range( self['pulsesInFamily']*self['numberOfAverages']):
            pulseFamily = np.mod( pulseGroup, self['pulsesInFamily'])
            average_response_1[:,pulseFamily] += response_1[:,pulseGroup]*( response_flag[pulseGroup]==1)
            average_response_2[:,pulseFamily] += response_2[:,pulseGroup]*( response_flag[pulseGroup]==1)


        for pulseFamily in range( self['pulsesInFamily']):
            average_response_1[:,pulseFamily] /= rep_count[pulseFamily]
            average_response_2[:,pulseFamily] /= rep_count[pulseFamily]


        # Save back to class
        self.stimulus_1 = stimulus_1
        self.response_1 = average_response_1
        self.stimulus_2 = stimulus_2
        self.response_2 = average_response_2


    def fetch_total_time( self):
        '''Returns maximum time of protocol'''
        return self['preTime'] + self['stimTime'] \
               + self['intervalTime'] \
               + self['stimTime'] + self['tailTime']


    def plot_stimulus( self, ax):
        '''Plots stimulus'''
        for i in range( self['pulsesInFamily']):
            ax.plot( self.time, self.stimulus_1[:,i], lw=1.0, color=self.cmap_1[i])
            ax.plot( self.time, self.stimulus_2[:,i], lw=1.0, color=self.cmap_2[i])


    def plot_response( self, ax):
        '''Plots response based on stimulus pulses'''
        for i in range( self['pulsesInFamily']):
            ax.plot( self.time, self.response_1[:,i], lw=0.3, color=self.cmap_1[i])
            ax.plot( self.time, self.response_2[:,i], lw=0.3, color=self.cmap_2[i])


    def plot_gap_IV_curve( self, named_pars, folder_name=None):
        '''Plots steady state IV curve'''
        fig, ax = plt.subplots( figsize=(12,8))
        plot_pars = {}
        plot_pars = self.fetch_plot_pars( plot_pars, named_pars)

        ax.set_xlabel( 'Transjunctional potential (mV)')
        ax.set_ylabel( 'Current (pA/pF)')

        stimulus, test_response_1, test_response_2 = \
        self.compute_gap_junction_current()

        ax.plot( stimulus, test_response_1, color='dodgerblue', lw=4)
        ax.plot( stimulus, test_response_2, color='orange', lw=4)

        self.add_title( ax, plot_pars)

        if folder_name: self.save_fig( fig, folder_name, 'gap_IV_curve')


    def compute_gap_junction_current( self, data=None):
        '''Compute gap junction conductance'''

        base_ind = ( self.time < self['preTime'])

        start_time_1 = self['preTime'] + self['stimTime']/2.0
        start_time_2 = self['preTime'] + self['stimTime'] \
                + self['intervalTime'] + self['stimTime']/2.0
        stop_time_1 = self['preTime'] + self['stimTime']
        stop_time_2 = self['preTime'] + self['stimTime'] \
                + self['intervalTime'] + self['stimTime']

        test_ind_1 = ( self.time > start_time_1) & ( self.time < stop_time_1)
        test_ind_2 = ( self.time > start_time_2) & ( self.time < stop_time_2)

        stimulus = np.mean( self.stimulus_1[test_ind_1,:], \
                axis=0)-self['holdingValue']

        base_response_1 = np.mean( self.response_2[base_ind,:], axis=0)
        test_response_1 = np.mean( self.response_2[test_ind_1,:], axis=0)
        base_response_2 = np.mean( self.response_1[base_ind,:], axis=0)
        test_response_2 = np.mean( self.response_1[test_ind_2,:], axis=0)

        test_response_1 -= base_response_1
        test_response_2 -= base_response_2
        #test_response_1 /= self.membrane_capacitance_1
        #test_response_2 /= self.membrane_capacitance_2

        if np.any( np.abs( test_response_1) == np.inf):
            test_response_1[:] = np.nan


        if np.any( np.abs( test_response_2) == np.inf):
            test_response_2[:] = np.nan


        if data is not None:
            for stim, resp1, resp2 in zip( stimulus, test_response_1, test_response_2):

                if stim in data.keys():
                    data[stim] = np.append( data[stim], [[ resp1, resp2]])
                else:
                    data[stim] = np.array( [[resp1, resp2]])

        return stimulus, test_response_1, test_response_2


    def compute_gap_junction_conductance( self, data):
        '''Compute conductances using transjunctional potentials'''
        self.compute_gap_junction_current( data)
        for key in data.keys():
            if key == 0:
                data[key] = np.zeros( shape=data[key].shape)
            else:
                data[key] /= -key

            inf_ind = ( np.abs( data[key]) == np.inf)
            data[key][inf_ind] = np.nan


    def compute_gap_junction_conductance_slope( self, data=None):
        '''Compute gap junction conductance using slope of response for single cell'''
        stimulus, response_1, response_2 = self.compute_gap_junction_current()

        X = np.array( [ np.ones( shape=stimulus.shape), stimulus])
        conductance = np.zeros( shape=(2,))

        if ( np.all( response_1 != np.nan)):
            conductance[0] = np.linalg.lstsq( X.transpose(), response_1, rcond=None)[0][1]


        if ( np.all( response_2 != np.nan)):
            conductance[1] = np.linalg.lstsq( X.transpose(), response_2, rcond=None)[0][1]


        if np.any( conductance != 0):
            if data is not None:
                data[0] = np.append( data[0], conductance)


        return -np.nanmean( conductance)
