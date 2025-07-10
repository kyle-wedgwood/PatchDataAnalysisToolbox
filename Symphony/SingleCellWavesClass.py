import numpy as np
from scipy.signal import find_peaks
from AbstractProtocolClass import AbstractProtocol
from matplotlib import pyplot as plt
import matplotlib as mpl

class SingleCellWaves(AbstractProtocol):
    '''Class for PulseFamily protocol analysis'''

    def __init__(self, epoch_group_object, block_uuid, count):
        super(SingleCellWaves, self).__init__( epoch_group_object, block_uuid, count)
        self.name = 'SingleCellWaves'


    def load_data(self):
        '''Loads data into array'''
        setattr(self, 'noIncrements', int(self['noIncrements']))
        setattr(self, 'pulsesInFamily', int(self['pulsesInFamily']))
        response = np.zeros(shape=(self['noPts'], self['noIncrements']))
        stimulus = np.ones(shape=(self['noPts']))*self['holdingValue']

        include_flag = np.zeros(shape=(self['noIncrements']))
        response_flag = np.zeros(shape=(self['noIncrements']))

        # Create reference stimuli
        for pulseFamily in range(self['pulsesInFamily']):
            pulse_start = self['preTime'] + pulseFamily*(self['pulseTime'] + self['interval'])
            pulse_end = pulse_start + self['pulseTime']
            stim_ind = (self.time > pulse_start) & (self.time < pulse_end)

            stimulus[stim_ind] += self['amplitude']


        # Count how many completed runs there are
        no_epochs = len(self.child_list)
        no_completed_runs = int(no_epochs/(self['noIncrements']))

        # Now establish which epochs to include based on rep count (assumes that
        # epochs are ordered)
        if no_completed_runs < 1:
            include_flag[:self['noIncrements']] = 1
        else:
            include_flag[:no_completed_runs*self['noIncrements']] = 1

        for epoch_no, epoch in enumerate(self.child_list):
            if include_flag[epoch_no]:
                response[:,epoch_no] = epoch.fetch_response()
                response_flag[epoch_no] = 1


        # Save back to class
        self.stimulus = stimulus
        self.response = response


    def fetch_total_time(self):
        '''Returns maximum time of protocol'''
        return self['preTime'] \
            + self['pulseTime'] \
            + (self['pulsesInFamily']-1)*(self['pulseTime'] + self['interval']) \
            + self['tailTime']


    def plot_stimulus(self, ax):
        '''Plots response based on stimulus pulses'''
        ax.plot( self.time, self.stimulus, lw=1.0, color='black')


    def plot_response(self, ax, ind=0):
        '''At present, just plot first response'''
        tau_2 = self['synTau_2']+ind*self['delayIncrement']
        tau_1 = self['synTau_1']
        ntau = int(np.ceil(tau_1/1000*self['sampleRate']))
        ntrip = int(self['noPts']/ntau)
        response = self.response[0:ntau*ntrip,ind]
        response_over_trips = response.reshape((ntrip,ntau))
        im = ax.pcolor(response_over_trips, vmin=-65, vmax=15)
        cb = plt.colorbar(im)
        cb.set_label('Voltage (mV)', rotation=270)
        ax.set_xlabel('Time (s)')
        tix = ax.get_xticks()
        ax.set_xticks(tix)
        ax.set_xticklabels(tix/self['sampleRate'])
        ax.set_ylabel('Rounddrip no.')
        ax.set_title('$\\tau_2$ = %d' % tau_2)


    def plot_ISIs(self, plot_all=True):
        '''Plot ISIs as a function of tau_2'''
        fig, ax = plt.subplots()
        blues = mpl.colormaps['Blues'].resampled(8)
        for epoch_no in range(self.response.shape[1]):
            tau = self['synTau_2'] + epoch_no*self['delayIncrement']
            peaks,_ = find_peaks(self.response[:,epoch_no], \
                                 height=-10, prominence=5)
            ISIs = np.diff(peaks)*1000/self['sampleRate']
            if plot_all:
                ax.scatter(tau*np.ones(len(ISIs)), ISIs, c=blues(np.linspace(0, 1, len(ISIs))))
    
        ax.set_xlabel('tau (ms)')
        ax.set_ylabel('ISI (ms)')
        ax.set_title(self.id)

        return fig, ax