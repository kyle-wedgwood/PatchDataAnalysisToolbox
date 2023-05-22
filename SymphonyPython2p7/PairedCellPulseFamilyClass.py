import numpy as np
from AbstractProtocolClass import AbstractProtocol
from matplotlib import pyplot as plt

class PairedCellPulseFamilyDC( AbstractProtocol):
    '''Class for PairedCellPulseFamilyDC analysis'''

    def __init__( self, epoch_group_object, block_uuid, count):
        super( PairedPulseFamily, self).__init__( epoch_group_object, block_uuid, count)
        self.name = 'PairedCellPulseFamilyDC'

        # Load properties into class object - NEED TO FIX THIS
        properties_group = self.group.get( 'properties')
        if properties_group:
            properties = properties_group.attrs

            for prop_pair in properties.items():
                setattr( self, prop_pair[0], prop_pair[1])
                self.pdf_vars.update( { prop_pair[0]: prop_pair[1]})
                #TO HERE


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

        response_1 = np.zeros(shape=(self['noPts'], self['numberOfAverages']))
        response_2 = np.zeros(shape=(self['noPts'], self['numberOfAverages']))
        leak_sub_response_1 = np.zeros(shape=(self['noPts'], 1))
        leak_sub_response_2 = np.zeros(shape=(self['noPts'], 1))
        stimulus_1 = np.zeros(shape=(self['noPts'], 1))
        stimulus_2 = np.zeros(shape=(self['noPts'], 1))

        include_flag = np.zeros(shape=(self['numberOfAverages']))
        response_flag = np.zeros(shape=(self['numberOfAverages']))

        # Cell 1
        rep_count = 0
        pre_ind = (self.time < self['preTime1'])
        time = self['preTime1']
        for pulseNo in range(self['numPulses1']):
            stim_ind = (self.time > time) & (self.time < time +
                        self['firstPulseDuration1'] \
                + (pulseNo-1)*self['pulseTimeIncrement1'])
            stimulus_1[stim_ind] = self['firstPulseAmp1'] +
                (pulseNo-1)*self['pulseAmpIncrement1']
            time += self['firstPulseDuration1'] \
                + (pulseNo-1)*self['pulseTimeIncrement1']) + \
                + self['firstInterval1'] +
                (pulseNo-1)*self['intervalIncrement1']`


        stimulus_1 += self['holdingValue']

        # Cell 2
        pre_ind = (self.time < self['preTime2'])
        time = self['preTime2']
        for pulseNo in range(self['numPulses2']):
            stim_ind = (self.time > time) & (self.time < time +
                        self['firstPulseDuration2'] \
                + (pulseNo-1)*self['pulseTimeIncrement2'])
            stimulus_1[stim_ind] = self['firstPulseAmp2'] +
                (pulseNo-1)*self['pulseAmpIncrement2']
            time += self['firstPulseDuration2'] \
                + (pulseNo-1)*self['pulseTimeIncrement2']) + \
                + self['firstInterval2'] +
                (pulseNo-1)*self['intervalIncrement2']`


        stimulus_2 += self['holdingValue']

        # Count how many completed runs there are
        if 'numPrePulses' not in self.__dict__.keys():
            self.numPrePulses = 0

        no_epochs = len(self.child_list)
        no_completed_runs = int(no_epochs/(self['numPrePulses']+1))

        # Now establish which epochs to include based on rep count (assumes that
        # epochs are ordered)
        if no_completed_runs < 1:
            include_flag[0] = 1

        else:
            include_Flag[:no_completed_runs] = 1


        for epoch_no, epoch in enumerate(self.child_list):

            stim_pars = epoch.fetch_stimulus_pars()
            stim_prop = epoch.fetch_stimulus_properties()

            pulseGroup = int(stim_prop.get('pulseGroup'))-1 # subtract 1 to index from zero

            pulse_end = time # time fetched from earlier

            pre_time = np.min(self['preTime1'], self['preTime2'])
            pre_ind = (self.time < pre_time)
            ind = (self.time < pulse_end)
            ind = np.where(ind)
            pre_ind = np.where(pre_ind)

            if include_flag[pulseGroup]:
                temp_response_1 = epoch.fetch_response(amp='Amp1')
                temp_response_2 = epoch.fetch_response(amp='Amp2')

                if stim_prop.get('pulseType') == 'pre':
                    response_1[ind,pulseGroup] += temp_response_1 - np.mean(
                            temp_response_1[pre_ind])
                    response_2[ind,pulseGroup] += temp_response_2 - np.mean(
                            temp_response_2[pre_ind])

                elif stim_prop.get('pulseType') == 'test':
                    response_1[ind,pulseGroup] += temp_response_1
                    response_2[ind,pulseGroup] += temp_response_2
                    response_flag[pulseGroup] = 1
                    rep_count += 1

                else:
                    response_1[ind,pulseGroup] = temp_response_1
                    response_2[ind,pulseGroup] = temp_response_2
                    response_flag[pulseGroup] = 1
                    rep_count += 1


        # Do averaging
        for pulseGroup in range(self['numberOfAverages']):
            leak_sub_response_1 += response_1[:,pulseGroup]*( response_flag[pulseGroup]==1)
            leak_sub_response_2 += response_2[:,pulseGroup]*( response_flag[pulseGroup]==1)


        for pulseFamily in range( self['pulsesInFamily']):
            if all( leak_sub_response_1 == 0.0):
                leak_sub_response_1 = np.nan
                leak_sub_response_2 = np.nan
            else:
                leak_sub_response_1 /= rep_count
                leak_sub_response_2 /= rep_count


        # Save back to class
        self.stimulus_1 = stimulus_1
        self.stimulus_2 = stimulus_2
        self.response_1 = leak_sub_response_1
        self.response_2 = leak_sub_response_2


    def fetch_total_time( self):
        '''Returns maximum time of protocol'''
        time = self['preTime1']
        for pulseNo in range(self['numPulses1']):
            time += self['firstPulseDuration1'] +
            (pulseNo-1)*self['pulseTimeIncrement1']
            time += self['firstInterval1'] +
            (pulseNo-1)*self['intervalIncrement1']

        time += self['tailTime1']
        return time


    def plot_stimulus(self, ax):
        '''Plots stimulus pulses'''
        ax.plot(self.time, self.stimulus_1, lw=1.0, color=self.cmap_1[i])
        ax.plot(self.time, self.stimulus_2, lw=1.0, color=self.cmap_2[i])


    def plot_response(self, ax):
        '''Plots response based on stimulus pulses'''
        ax.plot(self.time, self.response_1, lw=0.3, color=self.cmap_1[i])
        ax.plot(self.time, self.response_2, lw=0.3, color=self.cmap_2[i])
