import numpy as np
from AbstractProtocolClass import AbstractProtocol
from matplotlib import pyplot as plt

class SlowInactivationFamily( AbstractProtocol):
    '''Class for SlowInactivationFamily analysis'''

    def __init__( self, epoch_group_object, block_uuid, count):
        super( SlowInactivationFamily, self).__init__( epoch_group_object, block_uuid, count)
        self.name = 'SlowInactivationFamily'


    def load_data( self):
        '''Loads data into array'''
        duration_ref = np.array( range( \
        self['pulsesInFamily']))*self['durationIncrementPerPulse'] + \
        self['firstPulseDuration']

        response = np.zeros( shape=( self['noPts'], self['pulsesInFamily']*self['numberOfAverages']))
        leak_sub_response = np.zeros( shape=( self['noPts'], self['pulsesInFamily']))
        stimulus = np.zeros( shape=( self['noPts'], self['pulsesInFamily']))

        include_flag = np.zeros( shape=( self['pulsesInFamily']*self['numberOfAverages']))
        response_flag = np.zeros( shape=( self['pulsesInFamily']*self['numberOfAverages']))

        pre_ind = (self.time < self['preTime'])

        rep_count = np.zeros( shape=( self['pulsesInFamily']))

        for pulseFamily in range( self['pulsesInFamily']):
            first_stim_ind = (self.time > self['preTime']) \
                & (self.time < self['preTime'] + self['firstPulseDuration'] \
                + (pulseFamily-1)*self['durationIncrementPerPulse'])
            pulse_start = self['preTime'] + self['firstPulseDuration'] \
                + (pulseFamily-1)*self['durationIncrementPerPulse'] \
                + self['pulseInterval']
            second_stim_ind = (self.time > pulse_start) & \
                (self.time < pulse_start + self['testPulseDuration'])

            stimulus[first_stim_ind,pulseFamily]  = self['pulseAmplitude']
            stimulus[second_stim_ind,pulseFamily] = self['pulseAmplitude']


        stimulus += self['holdingValue']

        # Count how many completed runs there are
        if 'numPrePulses' not in self.__dict__.keys():
            self.numPrePulses = 0

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


        for epoch_no, epoch in enumerate( list( self.child_list)):

            stim_pars = epoch.fetch_stimulus_pars()
            stim_prop = epoch.fetch_stimulus_properties()

            if 'pulseGroup' in stim_prop.keys():
                pulseGroup = int( stim_prop.get( 'pulseGroup'))-1 # subtract 1 to index from zero
                pulseFamily = np.mod( pulseGroup, self['pulsesInFamily'])
            else:
                pulse_time = stim_pars['pulseTime']
                pulseFamily = np.argmin( (duration_ref - pulse_time)**2)
                pulseGroup = pulseFamily
                while response_flag[pulseGroup] == 1:
                    pulseGroup += self['pulsesInFamily']

            pulse_end = self['preTime'] + self['firstPulseDuration'] \
                + pulseFamily*self['durationIncrementPerPulse'] \
                + self['pulseInterval'] + self['testPulseDuration'] \
                + self['tailTime']

            pre_ind = (self.time < self['preTime'])
            ind = (self.time < pulse_end)

            pre_ind = np.where( pre_ind)
            ind = np.where( ind)

            if include_flag[pulseGroup]:
                temp_response = epoch.fetch_response()

                if stim_prop.get( 'pulseType') == 'pre':
                    response[ind,pulseGroup] += temp_response - np.mean( temp_response[pre_ind])

                elif stim_prop.get( 'pulseType') == 'test':
                    response[ind,pulseGroup] += temp_response
                    response_flag[pulseGroup] = 1
                    rep_count[pulseFamily] += 1

                else:
                    response[ind,pulseGroup] = temp_response
                    response_flag[pulseGroup] = 1
                    rep_count[pulseFamily] += 1


        # Do averaging
        for pulseGroup in range( self['pulsesInFamily']*self['numberOfAverages']):
            i = np.mod( pulseGroup, self['pulsesInFamily'])
            leak_sub_response[:,i] += response[:,pulseGroup]*( response_flag[pulseGroup]==1)


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
        return self['preTime'] + \
            self['firstPulseDuration'] + \
            self['durationIncrementPerPulse'] * (self['pulsesInFamily'] - 1) + \
            self['pulseInterval'] + \
            self['testPulseDuration'] + \
            self['tailTime']

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


    def plot_slow_inactivation_recovery( self, named_pars, sign=1, folder_name=None):
        '''Plots slow recovery from inactivation'''
        fig, ax = plt.subplots( figsize=(12,8))
        plot_pars = {}
        plot_pars = self.fetch_plot_pars( plot_pars, named_pars)

        ax.set_xlabel( 'Pulse duration (ms)')
        ax.set_ylabel( 'Current ratio)')

        durations, response = self.compute_peak_current_ratio_slow( sign=sign)

        ax.plot( durations, response, color='black', lw =4)

        self.add_title( ax, plot_pars)

        if folder_name: self.save_fig( fig, folder_name, 'slow_inactivation_recovery')


    def compute_peak_current_ratio_slow( self, data=None, sign=1):
        '''Compute current ratio of post and pre pulse'''
        base_ind = ( self.time < self['preTime'])
        offset = 10.0/self['sampleRate']

        durations = np.zeros( shape=( self['pulsesInFamily']))
        current_ratios = np.zeros( shape=( self['pulsesInFamily']))

        for pulse_no in range( self['pulsesInFamily']):
            duration = pulse_no*self['durationIncrementPerPulse'] + \
                self['firstPulseDuration']

            durations[pulse_no] = duration

            start_time = self['preTime']
            stop_time  = self['preTime'] + duration
            P1_ind = ( self.time > start_time+offset) & ( self.time < stop_time)

            start_time = self['preTime'] + duration \
                    + self['pulseInterval']
            stop_time = start_time + duration \
                    + self['pulseInterval'] + self['testPulseDuration']
            P2_ind = ( self.time > start_time+offset) & ( self.time < stop_time)

            base_current = sign*np.max( sign*self.response[base_ind,pulse_no])

            P1_current = sign*np.max( sign*self.response[P1_ind,pulse_no])
            P1_current -= base_current

            P2_current = sign*np.max( sign*self.response[P2_ind,pulse_no])
            P2_current -= base_current

            current_ratio = P2_current/P1_current
            current_ratios[pulse_no] = current_ratio

            if data is not None:
                if duration in data.keys():
                    data[duration] = np.append( data[duration], current_ratio)
                else:
                    data[duration] = current_ratio*np.ones( shape=(1))


        return durations, current_ratios
