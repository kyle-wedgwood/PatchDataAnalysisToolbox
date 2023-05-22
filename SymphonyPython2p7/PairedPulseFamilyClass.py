import numpy as np
from AbstractProtocolClass import AbstractProtocol
from matplotlib import pyplot as plt

class PairedPulseFamily( AbstractProtocol):
    '''Class for PairedPulseFamily analysis'''

    def __init__( self, epoch_group_object, block_uuid, count):
        super( PairedPulseFamily, self).__init__( epoch_group_object, block_uuid, count)
        self.name = 'PairedPulseFamily'

        # Load properties into class object - NEED TO FIX THIS
        properties_group = self.group.get( 'properties')
        if properties_group:
            properties = properties_group.attrs

            for prop_pair in properties.items():
                setattr( self, prop_pair[0], prop_pair[1])
                self.pdf_vars.update( { prop_pair[0]: prop_pair[1]})
                #TO HERE


    def load_data( self):
        '''Loads data into array'''
        interval_ref = np.array( range( \
        self['pulsesInFamily']))*self['intervalIncrementPerPulse'] + \
        self['firstInterval']

        response = np.zeros( shape=( self['noPts'], self['pulsesInFamily']*self['numberOfAverages']))
        leak_sub_response = np.zeros( shape=( self['noPts'], self['pulsesInFamily']))
        stimulus = np.zeros( shape=( self['noPts'], self['pulsesInFamily']))

        include_flag = np.zeros( shape=( self['pulsesInFamily']*self['numberOfAverages']))
        response_flag = np.zeros( shape=( self['pulsesInFamily']*self['numberOfAverages']))

        pre_ind = (self.time < self['preTime'])
        first_stim_ind = (self.time > self['preTime']) \
            & (self.time < self['preTime'] + self['pulseTime'])

        rep_count = np.zeros( shape=( self['pulsesInFamily']))

        for pulseFamily in range( self['pulsesInFamily']):
            pulse_start = self['preTime'] + self['pulseTime'] \
                + self['firstInterval'] + pulseFamily*self['intervalIncrementPerPulse']
            second_stim_ind = (self.time > pulse_start) & \
                (self.time < pulse_start + self['pulseTime'] \
                + self['pulseTimeIncrement'])

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


        for epoch_no, epoch in enumerate( self.child_list):

            stim_pars = epoch.fetch_stimulus_pars()
            stim_prop = epoch.fetch_stimulus_properties()
            stim_interval = stim_pars['pulseInterval']

            if 'pulseGroup' in stim_prop.keys():
                pulseGroup = int( stim_prop.get( 'pulseGroup'))-1 # subtract 1 to index from zero
                pulseFamily = np.mod( pulseGroup, self['pulsesInFamily'])
                #stim_interval = stim_pars.get( 'intervalTime')
            else:
                pulseFamily = np.argmin( (interval_ref - stim_interval)**2)
                pulseGroup = pulseFamily
                while response_flag[pulseGroup] == 1:
                    pulseGroup += self['pulsesInFamily']


            pulse_end = self['preTime'] + self['pulseTime'] \
                + stim_interval + self['pulseTime'] \
                + self['pulseTimeIncrement'] + self['tailTime']

            pre_ind = (self.time < self['preTime'])
            ind = (self.time < pulse_end)

            if include_flag[pulseGroup]:
                temp_response = epoch.fetch_response()

                ind = np.where(ind)
                pre_ind = np.where(pre_ind)

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
        return self['preTime'] + self['pulseTime'] + self['firstInterval'] + \
            self['intervalIncrementPerPulse']*( self['pulsesInFamily']-1) + \
            self['pulseTime'] + self['pulseTimeIncrement'] + self['tailTime']


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


    def plot_inactivation_recovery( self, named_pars, sign=1, folder_name=None):
        '''Plots recovery from inactivation'''
        fig, ax = plt.subplots( figsize=(12,8))
        plot_pars = {}
        plot_pars = self.fetch_plot_pars( plot_pars, named_pars)

        ax.set_xlabel( 'Interval (ms)')
        ax.set_ylabel( 'Current ratio)')

        intervals, response = self.compute_peak_current_ratio_fast( sign=sign)

        ax.plot( intervals, response, color='black', lw =4)

        self.add_title( ax, plot_pars)

        if folder_name: self.save_fig( fig, folder_name, 'inactivation_recovery')


    def compute_peak_current_ratio_fast( self, data=None, sign=1):
        '''Compute current ratio of post and pre pulse'''
        base_ind = ( self.time < self['preTime'])
        offset = 10.0/self['sampleRate']

        start_time = self['preTime']
        stop_time  = self['preTime'] + self['pulseTime']

        P1_ind = ( self.time > start_time+offset) & ( self.time < stop_time)

        intervals = np.zeros( shape=( self['pulsesInFamily']))
        current_ratios = np.zeros( shape=( self['pulsesInFamily']))

        for pulse_no in range( self['pulsesInFamily']):
            interval = pulse_no*self['intervalIncrementPerPulse'] + \
                self['firstInterval']

            intervals[pulse_no] = interval

            start_time = self['preTime'] + self['pulseTime'] \
                    + interval
            stop_time = start_time + self['pulseTime'] \
                    + self['pulseTimeIncrement']

            P2_ind = ( self.time > start_time+offset) & ( self.time < stop_time)

            base_current = sign*np.max( sign*self.response[base_ind,pulse_no])

            P1_current = sign*np.max( sign*self.response[P1_ind,pulse_no])
            P1_current -= base_current

            P2_current = sign*np.max( sign*self.response[P2_ind,pulse_no])
            P2_current -= base_current

            current_ratio = P2_current/P1_current

            current_ratios[pulse_no] = current_ratio

            if data is not None:
                if interval in data.keys():
                    data[interval] = np.append( data[interval], current_ratio)
                else:
                    data[interval] = current_ratio*np.ones( shape=(1))


        return intervals, current_ratios

