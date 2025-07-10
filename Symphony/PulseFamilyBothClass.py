import numpy as np
from matplotlib import pyplot as plt
from AbstractProtocolClass import AbstractProtocol

class PulseFamilyBoth(AbstractProtocol):
    '''Class for PulseFamilyBoth analysis'''

    def __init__(self, epoch_group_object, block_uuid, count):
        super(PulseFamilyBoth, self).__init__(epoch_group_object, block_uuid, count)
        self.name = 'PulseFamilyBoth'
        

    def load_data(self):
        '''Load data into array'''

        epoch = self.child_list[0] # Check that this works
        self.response_1 = epoch.fetch_response('Amp1')
        self.response_2 = epoch.fetch_response('Amp2')

        # Load dynamic clamp data if present
        try:
            self.dc_I_scale = 400.0
            self.dc_1 = self.dc_I_scale*epoch.fetch_response('DC1input')
            self.dc_2 = self.dc_I_scale*epoch.fetch_response('DC2input')
            self.teensyV_1 = epoch.fetch_response('teensy1input')
            self.teensyV_2 = epoch.fetch_response('teensy2input')
            self.dc_flag = True
            
        except:
            self.dc_flag = False

        ## Overwrite time as necessary
        #noPts = len(self.response_1)
        #self.time = np.array(range( noPts))/self['sampleRate']*1000.0


    def fetch_total_time( self):
        '''Returns maximum time of protocol'''
        
        # Fix issue with non-integer values for numPulses
        self.numPulses1 = int(self.numPulses1)
        self.numPulses2 = int(self.numPulses2)

        last_pulse_end_1 = self['preTime1'] + self['pulseTime1']
        for i in range(self['numPulses1']-1):
            last_pulse_end_1 += (self['intervalTime1'] \
                                 +i*self['intervalTimeIncrement1'] \
                                 +self['pulseTime1'] \
                                 +(i+1)*self['pulseTimeIncrement1'])


        last_pulse_end_2 = self['preTime2'] + self['pulseTime1'] 
        for i in range(self['numPulses2']-1):
            last_pulse_end_2 += (self['intervalTime2'] \
                                 +i*self['intervalTimeIncrement2'] \
                                 +self['pulseTime2'] \
                                 +(i+1)*self['pulseTimeIncrement2'])


        total_time = np.max([last_pulse_end_1,last_pulse_end_2])+self['tailTime']

        return total_time


    def plot_stimulus( self, ax):
        '''Required to overload base class function'''
        stimulus_1 = np.zeros(self['noPts'])
        stimulus_2 = np.zeros(self['noPts'])

        # Stimulus for cell 1
        pulse_start = self['preTime1']

        for i in range(self['numPulses1']):
            pulse_end = pulse_start + self['pulseTime1']+i*self['pulseTimeIncrement1']
            ind = (self.time > pulse_start) & (self.time < pulse_end)
            stimulus_1[ind] = self['amplitude1']+i*self['amplitudeIncrement1']
            pulse_start = pulse_end + self['intervalTime1']+i*self['intervalTimeIncrement1']

        for i in range(self['numPulses2']):
            pulse_end = pulse_start + self['pulseTime2']+i*self['pulseTimeIncrement2']
            ind = (self.time > pulse_start) & (self.time < pulse_end)
            stimulus_2[ind] = self['amplitude2']+i*self['amplitudeIncrement2']
            pulse_start = pulse_end + self['intervalTime2']+i*self['intervalTimeIncrement2']
            
        ax.plot(self.time, stimulus_1, lw=1, color='dodgerblue')
        ax.plot(self.time, stimulus_2, lw=1, color='orange')


    def plot_response(self, ax):
        '''Plots response'''
        ax.plot(self.time, self.response_1, lw=2, color='dodgerblue')
        ax.plot(self.time, self.response_2, lw=2, color='orange')


    def plot_dc_inputs(self, axR, axS):
        '''Plots inputs from dynamic clamp'''
        axR.plot(self.time, self.teensyV_1, lw=2, color='steelblue')
        axR.plot(self.time, self.teensyV_2, lw=2, color='peru')

        axS.plot(self.time, self.dc_1, lw=1, color='mediumpurple')
        axS.plot(self.time, self.dc_2, lw=1, color='orangered')


    def plot_stimuli_and_responses( self, protocol='all', named_pars=[], folder_name=None):
        '''Sets up figure and axis handle then calls plotting function'''
        if (protocol == 'all' or protocol == self.name):
            if self.operating_mode == 'VClamp':
                r_label = 'I (pA)'
                s_label = 'V (mV)'
            elif (self.operating_mode == 'IClamp') \
                    or (self.operating_mode == 'I0'):
                r_label = 'V (mV)'
                s_label = 'I (pA)'


            # Now find plot parameters
            plot_pars = {}
            plot_pars = self.fetch_plot_pars( plot_pars, named_pars)

            plt.rcParams.update({'font.size': 22})
            fig, (ax_S,ax_R) = plt.subplots(nrows=2, figsize=(24,8))

            ax_S.set_xlabel('Time (s)')
            ax_R.set_xlabel('Time (s)')

            self.plot_stimulus(ax_S)
            self.plot_response(ax_R)

            if self.dc_flag:
                self.plot_dc_inputs(ax_R, ax_S)
                ax_S.set_ylabel('I (pA)')
                ax_R.set_ylabel('V (mV)')

            else:
                ax_S.set_ylabel(s_label)
                ax_R.set_ylabel(r_label)


            fig_filename = self.post_process_figure(fig, ax_R, plot_pars, \
                 folder_name, 'stimulus_response')

            return fig_filename

