import numpy as np
from AbstractProtocolClass import AbstractProtocol
from matplotlib import pyplot as plt

class PulseFamily( AbstractProtocol):
    '''Class for PulseFamily protocol analysis'''

    def __init__( self, epoch_group_object, block_uuid, count):
        super( PulseFamily, self).__init__( epoch_group_object, block_uuid, count)
        self.name = 'PulseFamily'


    def load_data( self):
        '''Loads data into array'''
        response = np.zeros( shape=( self['noPts'], self['pulsesInFamily']*self['numberOfAverages']))
        averaged_response = np.zeros( shape=( self['noPts'], self['pulsesInFamily']))
        stimulus = np.ones( shape=( self['noPts'], self['pulsesInFamily']))*self['holdingValue']

        include_flag = np.zeros( shape=( self['pulsesInFamily']*self['numberOfAverages']))
        response_flag = np.zeros( shape=( self['pulsesInFamily']*self['numberOfAverages']))
        rep_count = np.zeros( shape=( self['pulsesInFamily']))

        ind = (self.time > self['preTime']) & (self.time < self['preTime'] + self['stimTime'])

        # Create reference stimuli
        stimulus_ref = np.zeros( self['pulsesInFamily'])
        for i in range( self['pulsesInFamily']):
            stimulus_ref[i] = self['firstPulseSignal']+i*self['incrementPerPulse']
            stimulus[ind,i] += stimulus_ref[i]


        # Count how many completed runs there are
        no_epochs = len( self.child_list)
        no_completed_runs = int( no_epochs/(self['pulsesInFamily']))

        # Now establish which epochs to include based on rep count (assumes that
        # epochs are ordered)
        if no_completed_runs < 1:
            include_flag[:self['pulsesInFamily']] = 1
            rep_count[:] = 1
        else:
            include_flag[:no_completed_runs*self['pulsesInFamily']] = 1
            rep_count[:] = no_completed_runs

        pulseGroup = -1 # For use in case stimulus is not changing in amplitude

        for epoch_no, epoch in enumerate( self.child_list):

            stim_pars = epoch.fetch_stimulus_pars()
            stim_amp  = stim_pars.get( 'amplitude')

            if self['incrementPerPulse'] == 0:
                pulseGroup += 1
            else:
                pulseFamily = np.argmin( (stimulus_ref - stim_amp)**2)
                pulseGroup = pulseFamily


            while response_flag[pulseGroup] == 1:
                pulseGroup += self['pulsesInFamily']


            if include_flag[pulseGroup]:
                response[:,pulseGroup] += epoch.fetch_response()
                response_flag[pulseGroup] = 1


        for pulseGroup in range( self['pulsesInFamily']*self['numberOfAverages']):
            pulseFamily = np.mod( pulseGroup, self['pulsesInFamily'])
            averaged_response[:,pulseFamily] += response[:,pulseGroup]*( response_flag[pulseGroup]==1)


        for pulseFamily in range( self['pulsesInFamily']):
            if np.all( averaged_response[:,pulseFamily] == 0.0):
                averaged_response[:,pulseFamily] = np.nan
            else:
                averaged_response[:,pulseFamily] /= rep_count[pulseFamily]


        # Save back to class
        self.stimulus = stimulus
        self.response = averaged_response


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


    def plot_response( self, ax):
        '''Plots response based on stimulus pulses'''
        cmap = np.linspace( 1, 0, self['pulsesInFamily']+1)
        cmap = cmap[1:]
        cmap = np.tile( cmap, (3,1))

        for i in range( self['pulsesInFamily']):
            ax.plot( self.time, self.response[:,i], lw=0.1, color=cmap[:,i])


    def plotIVCurve( self, start_time, stop_time, named_pars, folder_name=None):
        '''Plots mean current between [startTime,stopTime] against voltage'''
        fig, ax = plt.subplots( figsize=(12,8))
        plot_pars = {}
        plot_pars = self.fetch_plot_pars( plot_pars, named_pars)

        ax.set_xlabel( 'Voltage (mV)')
        ax.set_ylabel( 'I (pA)')

        ind = (self.time > start_time)*(self.time < stop_time)
        ax.plot( np.mean( self.stimulus[ind,:], axis=0), \
                 np.mean( self.response[ind,:], axis=0), color='black', lw=4)

        self.add_title( ax, plot_pars)

        if folder_name:
            self.save_fig( fig, folder_name, 'IVcurve')


    def compute_normalised_current( self, data=None, start_time=None, \
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


    def compute_normalised_peak_current( self, data=None, start_time=None, \
            stop_time=None, sign=1):
        '''Find peak inward current and normalise against cell membrane capacitance'''

        if not start_time:
            start_time = self['preTime']

        if not stop_time:
            stop_time  = self['preTime'] + self['stimTime']

        offset = 2.0/self['sampleRate']

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
