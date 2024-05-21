import matplotlib.pyplot as plt
from SeriesClass import Series

class CCAxon( Series):
    '''Class for GapFree analysis'''

    def __init__( self, exp_object, obj, index):
        '''Initialiser for GapFree class'''

        super( CCAxon, self).__init__( exp_object, obj, index)


    def plot_stimuli_and_responses( self, protocol='all', folder_name='.'):
        '''Plot responses'''

        if (protocol == 'all' or protocol == self.name):
            if self.recording_mode == 'VClamp':
                y_label = 'Current (A)'
            elif (self.recording_mode == 'IClamp') \
                    or (self.recording_mode == 'I0'):
                y_label = 'Voltage (V)'


            plt.rcParams.update({'font.size': 22})
            fig, ax = plt.subplots( figsize=(24,8))
            ax.set_xlabel( 'Time (%s)' % self.t_unit)
            ax.set_ylabel( y_label)

            plt.plot( self.time, self.data['Adc-1'], lw=2)
            ax.set_xlim( [self.time[0], self.time[-1]])

            plot_pars = {}

            fig_filename = self.post_process_figure( fig, ax, plot_pars, \
                    folder_name, 'stimulus_response')

            return fig_filename



