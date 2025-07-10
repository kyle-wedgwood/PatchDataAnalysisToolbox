import numpy as np
from AbstractProtocolClass import AbstractProtocol
from matplotlib import pyplot as plt
from scipy.optimize import minimize
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter

class PulseFamilyLeakSub( AbstractProtocol):
    '''Class for PulseFamilyLeakSub analysis'''

    def __init__( self, epoch_group_object, block_uuid, count):
        super( PulseFamilyLeakSub, self).__init__( epoch_group_object, block_uuid, count)
        self.name = 'PulseFamilyLeakSub'


    def load_data( self):
        '''Loads data into array'''
        response = np.zeros( shape=( self['noPts'], self['pulsesInFamily']*self['numberOfAverages']))
        leak_sub_response = np.zeros( shape=( self['noPts'],
            self['pulsesInFamily']))
        stimulus = np.ones( shape=( self['noPts'], self['pulsesInFamily']))*self['holdingValue']

        pre_ind  = (self.time < self['preTime'])
        stim_ind = (self.time > self['preTime']) & (self.time < self['preTime'] + self['stimTime'])

        include_flag = np.zeros( shape=( self['pulsesInFamily']*self['numberOfAverages']))
        response_flag = np.zeros( shape=( self['pulsesInFamily']*self['numberOfAverages']))
        rep_count = np.zeros( shape=( self['pulsesInFamily']))

        # Set stimulus
        for i in range( self['pulsesInFamily']):
            stimulus[stim_ind,i] += self['firstPulseSignal'] + i*self['incrementPerPulse']


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

        # Now load responses
        for epoch_no, epoch in enumerate( self.child_list):

            stim_pars = epoch.fetch_stimulus_pars()
            stim_prop = epoch.fetch_stimulus_properties()

            pulseGroup = int( stim_prop.get( 'pulseGroup'))-1 # subtract 1 to index from zero
            pulseFamily = np.mod( pulseGroup, self['pulsesInFamily'])

            if include_flag[pulseGroup]:
                temp_response = epoch.fetch_response()

                if stim_prop.get( 'pulseType') == b'pre':
                    response[:,pulseGroup] += temp_response - np.mean( temp_response[pre_ind])

                elif stim_prop.get( 'pulseType') == b'test':
                    response[:,pulseGroup] += temp_response
                    response_flag[pulseGroup] = 1


        for pulseGroup in range( self['pulsesInFamily']*self['numberOfAverages']):
            pulseFamily = np.mod( pulseGroup, self['pulsesInFamily'])
            leak_sub_response[:,pulseFamily] += response[:,pulseGroup]*( response_flag[pulseGroup]==1)


        for pulseFamily in range( self['pulsesInFamily']):
            if np.all( leak_sub_response[:,pulseFamily] == 0.0):
                leak_sub_response[:,pulseFamily] = np.nan
            else:
                leak_sub_response[:,pulseFamily] /= rep_count[pulseFamily]


        # Save back to class
        self.stimulus = stimulus
        self.response = leak_sub_response


    def plot_stimulus( self, ax):
        '''Plots response based on stimulus pulses'''
        cmap = np.linspace( 1, 0, self['pulsesInFamily']+1)
        cmap = cmap[1:]
        cmap = np.tile( cmap, (3,1))

        for i in range( self['pulsesInFamily']):
            ax.plot( self.time, self.stimulus[:,i], lw=1.0, color=cmap[:,i])


    def fetch_total_time( self):
        '''Returns maximum time of protocol'''
        return self['preTime'] + self['stimTime'] + self['tailTime']


    def plot_response( self, ax):
        '''Plots response based on stimulus pulses'''
        cmap = np.linspace( 1, 0, self['pulsesInFamily']+1)
        cmap = cmap[1:]
        cmap = np.tile( cmap, (3,1))

        for i in range( self['pulsesInFamily']):
            ax.plot( self.time, self.response[:,i], lw=0.1, color=cmap[:,i])


    def plot_mean_IV_curve( self, start_time, stop_time, named_pars, folder_name=None):
        '''Plots mean current between [startTime,stopTime] against voltage'''
        fig, ax = plt.subplots( figsize=(12,8))
        plot_pars = {}
        plot_pars = self.fetch_plot_pars( plot_pars, named_pars)

        ax.set_xlabel( 'Voltage (mV)')
        ax.set_ylabel( 'Current density (pA/pF)')

        stimulus, test_response = self.compute_normalised_current()

        ax.plot( stimulus, test_response, color='black', lw=4)

        self.add_title( ax, plot_pars)

        if folder_name: self.save_fig( fig, folder_name, 'IVcurve')


    def plot_peak_IV_curve( self, named_pars, sign=1, folder_name=None):
        '''Plots peak current'''
        fig, ax = plt.subplots( figsize=(12,8))
        plot_pars = {}
        plot_pars = self.fetch_plot_pars( plot_pars, named_pars)

        ax.set_xlabel( 'Voltage (mV)')
        ax.set_ylabel( 'Peak current density (pA/pF)')

        stimulus, peak_current = self.compute_normalised_peak_current( sign=sign)

        ax.plot( stimulus, peak_current, color='black', lw =4)

        self.add_title( ax, plot_pars)

        if folder_name: self.save_fig( fig, folder_name, 'peak_IV_curve')


    def compute_leak_sub_normalised_current( self, data=None, start_time=None, \
            stop_time=None, cell_exclude_list=[], protocol_exclude_list=[]):
        '''Find response current normalised against cell membrane capacitance'''
        if ( start_time == None):
            start_time = self['preTime'] + self['stimTime']/2.0
        if ( stop_time == None):
            stop_time  = self['preTime'] + self['stimTime']


        base_ind = ( self.time < self['preTime'])
        test_ind = ( self.time > start_time) & ( self.time < stop_time)

        stimulus = np.mean( self.stimulus[test_ind,:], axis=0)
        base_response = np.mean( self.response[base_ind,:], axis=0)
        test_response = np.mean( self.response[test_ind,:], axis=0)

        test_response -= base_response
        test_response /= self.membrane_capacitance

        if data is not None:
            for stim, resp in zip( stimulus, test_response):
                if stim in data.keys():
                    data[stim] = np.append( data[stim], resp)
                else:
                    data[stim] = resp*np.ones( shape=(1))


        return stimulus, test_response


    def compute_leak_sub_normalised_peak_current( self, data=None, sign=1):
        '''Find peak inward current and normalise against cell membrane capacitance'''

        start_time = self['preTime']
        stop_time  = self['preTime'] + self['stimTime']
        offset = 5.0/self['sampleRate']

        base_ind = ( self.time < self['preTime'])
        test_ind = ( self.time > start_time+offset) & ( self.time < stop_time)

        stimulus = np.mean( self.stimulus[test_ind,:], axis=0)
        base_current = sign*np.max( sign*self.response[base_ind,:],axis=0)
        peak_current = sign*np.max( sign*self.response[test_ind,:],axis=0)

        peak_current -= base_current
        peak_current /= self.membrane_capacitance

        if data is not None:
            for stim, resp in zip( stimulus, peak_current):
                if stim in data.keys():
                    data[stim] = np.append( data[stim], resp)
                else:
                    data[stim] = resp*np.ones( shape=(1))


        return stimulus, peak_current


    def compute_leak_sub_normalised_conductance( self, data, reversal_potential, sign=1):
        '''Compute conductances from currents'''

        self.compute_leak_sub_normalised_peak_current( data, sign)
        for key in data.keys():
            data[key] /= (key-reversal_potential)


    def plot_time_constants( self, named_pars, sign=1, folder_name=None):
        '''Compute inactivation time constants'''
        fig, ax = plt.subplots( figsize=(12,8))
        plot_pars = {}
        plot_pars = self.fetch_plot_pars( plot_pars, named_pars)

        ax.set_xlabel( 'Voltage (mV)')
        ax.set_ylabel( 'Time constant (ms)')

        stimulus, time_constants = self.compute_time_constants( sign=sign)

        ax.plot( stimulus, time_constants[:,0], color='blue', lw =4, label='activation')
        ax.plot( stimulus, time_constants[:,1], color='red', lw =4, label='fast inactivation')
        ax.plot( stimulus, time_constants[:,2], color='black', lw =4, label='slow inactivation')
        ax.legend()

        self.add_title( ax, plot_pars)

        if folder_name: self.save_fig( fig, folder_name, 'inactivation_time_constant')


    def compute_time_constants( self, data=None, sign=1, method='time'):
        '''Compute time constants for activation and inactivation'''

        start_time = self['preTime']
        stop_time  = self['preTime'] + self['stimTime']
        offset = 20/self['sampleRate']

        end_ind  = ( self.time > start_time + self['stimTime']/2.0) \
                    & ( self.time < stop_time)
        test_ind = ( self.time > start_time+offset) & ( self.time < stop_time)

        stimulus = np.mean( self.stimulus[test_ind,:], axis=0)
        end_current = np.mean( self.response[end_ind,:], axis=0)

        time_constants = np.zeros( shape=( self['pulsesInFamily'],3))
        scale = 0.67

        for pulse_no in range( self['pulsesInFamily']):

            time = self.time[test_ind]
            response = sign*( self.response[test_ind,pulse_no]-end_current[pulse_no])
            peak_response = np.max( response)
            peak_end_response = np.max( sign*( \
                self.response[end_ind,pulse_no]-end_current[pulse_no]))
            guess_inact = [ 1, 0.1, 1, 10, 0.1]
            guess_act   = [ 1, 0.0]

            if peak_response > 2.0*peak_end_response:

                peak_ind = np.argmax( response)

                # Activation time constants
                rise_ind = int( scale*peak_ind)
                rise_time = time[:rise_ind]
                rise_response = response[:rise_ind]

                if rise_ind > 10:
                    rise_time -= rise_time[0]
                    popt,pcov = curve_fit( self.Linear, rise_time, \
                            rise_response, p0=guess_act)

                    fig, ax = plt.subplots()
                    ax.plot( rise_time, rise_response, rise_time, \
                            self.Linear( rise_time, popt[0], \
                            popt[1]))
                    ax.set_title( ('%s') % (1.0/popt[0]))

                    #time_constants[pulse_no,0] = np.abs( popt[1])
                    time_constants[pulse_no,0] = 1.0/popt[0]

                    guess_act = popt


                # Inactivation time constants
                decay_response = response[peak_ind:]
                decay_time = time[peak_ind:]
                decay_time -= decay_time[0]

                plateau_ind = decay_response < 0.0
                plateau_ind = list( plateau_ind).index( True)

                plateau_ind = int( len( decay_time)/2.0)

                plateau_ind = self.find_plateau_ind( decay_response, \
                        method=method)

                decay_response = decay_response[:plateau_ind]
                decay_time = decay_time[:plateau_ind]

                if plateau_ind > 10:

                    popt,pcov = curve_fit( self.BiExponential, decay_time,
                            decay_response, p0=guess_inact)

                    fig, ax = plt.subplots()
                    ax.plot( decay_time, decay_response, decay_time, \
                    self.BiExponential( decay_time, popt[0], \
                            popt[1], popt[2], popt[3], popt[4]))
                    ax.set_title( ('%s, %s') % (popt[1],popt[3]))

                    tau = np.sort( [ popt[1], popt[3]])
                    if np.all( tau > 0.0):
                        time_constants[pulse_no,1] = tau[0]
                        time_constants[pulse_no,2] = tau[1]

                    guess_inact = popt


        if data is not None:
            for stim, time_constant in zip( stimulus, time_constants):
                if stim in data.keys():
                    data[stim] = np.append( data[stim], [ time_constant], axis=0)
                else:
                    data[stim] = [ time_constant]


        return stimulus, time_constants


    @staticmethod
    def find_plateau_ind( response, method='filtered', window=501, \
            order=5, thresh=0.05, fraction=2.0):
        '''Find plateaut by searching by zero value of filtered derivative'''

        if method == 'filtered':
            r_deriv = savgol_filter( response, window, order, deriv=1)

            plateau_ind = (r_deriv > thresh)
            plateau_ind = list( plateau_ind).index( True)

        elif method == 'val':

            plateau_ind = (response < thresh)
            plateau_ind = list( plateau_ind).index( True)

        elif method == 'time':

            plateau_ind = int( len( response)/fraction)


        return plateau_ind
