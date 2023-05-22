import numpy as np
from AbstractProtocolClass import AbstractProtocol
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit

class TailPulseFamily( AbstractProtocol):
    '''Class for TailPulseFamily analysis'''

    def __init__( self, epoch_group_object, block_uuid, count):
        super( TailPulseFamily, self).__init__( epoch_group_object, block_uuid, count)
        self.name = 'TailPulseInactivation'


    def load_data( self):
        '''Loads data into array'''
        stimulus_ref = np.array( range( \
            self['pulsesInFamily']))*self['incrementPerPulse'] + \
            self['firstPulseSignal']

        response = np.zeros( shape=( self['noPts'], self['pulsesInFamily']*self['numberOfAverages']))
        leak_sub_response = np.zeros( shape=( self['noPts'], self['pulsesInFamily']))
        stimulus = np.zeros( shape=( self['noPts'], self['pulsesInFamily']))

        pre_ind  = (self.time < self['preTime'])
        stim_ind = (self.time > self['preTime']) & (self.time < self['preTime'] + self['stimTime'])
        test_ind = (self.time > self['preTime'] + self['stimTime']) \
            & (self.time < self['preTime'] + self['stimTime'] + self['testTime'])

        include_flag = np.zeros( shape=( self['pulsesInFamily']*self['numberOfAverages']))
        response_flag = np.zeros( shape=( self['pulsesInFamily']*self['numberOfAverages']))
        rep_count = np.zeros( shape=( self['pulsesInFamily']))

        for i in range( self['pulsesInFamily']):
            stimulus[stim_ind,i] = self['preAmplitude']
            stimulus[test_ind,i] = self['firstPulseSignal'] + i*self['incrementPerPulse']

        stimulus += self['holdingValue']

        # Count how many completed runs there are
        no_epochs = len( self.child_list)

        no_completed_runs = int( no_epochs/(self['pulsesInFamily']*(self['numPrePulses']+1)))

        # Now establish which epochs to include based on rep count (assumes that
        # epochs are ordered)
        if no_completed_runs < 1:
            include_flag[:self['pulsesInFamily']] = 1
            rep_count[:] = 1
        else:
            include_flag[:no_completed_runs*self['pulsesInFamily']] = 1
            rep_count[:] = no_completed_runs


        for epoch_no, epoch in enumerate( self.child_list):

            stim_pars = epoch.fetch_stimulus_pars()
            stim_prop = epoch.fetch_stimulus_properties()
            stim_amp  = stim_pars.get( 'amplitude')

            if 'pulseGroup' in stim_prop.keys():
                pulseGroup = int( stim_prop.get( 'pulseGroup'))-1 # subtract 1 to index from zero
                pulseFamily = np.mod( pulseGroup, self['pulsesInFamily'])
                #stim_interval = stim_pars.get( 'intervalTime')
            else:
                pulseFamily = np.argmin( (stimulus_ref - stim_amp)**2)
                pulseGroup = pulseFamily
                while response_flag[pulseGroup] == 1:
                    pulseGroup += self['pulsesInFamily']


            if include_flag[pulseGroup]:
                temp_response = epoch.fetch_response()

                if stim_prop.get( 'pulseType') == 'pre':
                    response[:,pulseGroup] += temp_response - np.mean( temp_response[pre_ind])

                elif stim_prop.get( 'pulseType') == 'test':
                    response[:,pulseGroup] += temp_response
                    response_flag[pulseGroup] = 1

                else:
                    response[:,pulseGroup] = temp_response
                    response_flag[pulseGroup] = 1


        for pulseGroup in range( self['pulsesInFamily']*self['numberOfAverages']):
            pulseFamily = np.mod( pulseGroup, self['pulsesInFamily'])
            leak_sub_response[:,pulseFamily] += response[:,pulseGroup]*( response_flag[pulseGroup]==1)


        for pulseFamily in range( self['pulsesInFamily']):
            if all( leak_sub_response[:,pulseFamily] == 0.0):
                leak_sub_response[:,pulseFamily] = np.nan
            else:
                leak_sub_response[:,pulseFamily] /= rep_count[pulseFamily]


        # Save back to class
        self.stimulus = stimulus
        self.response = leak_sub_response


    def fetch_total_time( self):
        '''Returns maximum time of protocol'''
        return self['preTime'] + self['stimTime'] \
               + self['testTime'] + self['tailTime']


    def plot_stimulus( self, ax):
        '''Plots response based on stimulus pulses'''
        cmap = np.linspace( 1, 0, self['pulsesInFamily']+1)
        cmap = cmap[1:]
        cmap = np.tile( cmap, (3,1))

        for i in range( self['pulsesInFamily']):
            ax.plot( self.time, self.stimulus[:,i], lw=1.0, color=cmap[:,i])


    def plot_response( self, ax):
        '''Plots response based on stimulus pulses'''
        cmap = np.linspace( 1, 0, self['pulsesInFamily']+1)
        cmap = cmap[1:]
        cmap = np.tile( cmap, (3,1))

        for i in range( self['pulsesInFamily']):
            ax.plot( self.time, self.response[:,i], lw=0.1, color=cmap[:,i])


    def compute_K_reversal_potential( self, data):
        '''Compute reversal potential by searching for change in sign of
        exponent in exponential fit to tail currents'''

        start_time = self['preTime'] + self['stimTime']
        stop_time  = start_time + self['testTime']

        test_ind = (self.time >= start_time) & ( self.time < stop_time)
        time = self.time[test_ind] - start_time

        guess = np.zeros( 3)
        exponents = np.zeros( self['pulsesInFamily'])

        for pulse_no in range( self['pulsesInFamily']):
            test_resp = self.response[test_ind,pulse_no]
            popt,pcov = curve_fit( self.OffsetExponential, time,
                            test_resp, p0=guess)

            exponents[pulse_no] = popt[0]
            guess = popt


        zero_ind = (exponents[1:] > 0.0) & (exponents[:-2] < 0.0)
        zero_ind = np.where( zero_ind)[0]

        self.E_K = self['firstPulseSignal'] + zero_ind*self['incrementPerPulse'] \
                + self['holdingValue']

        data[0] = np.append( data[0], self.E_K)

