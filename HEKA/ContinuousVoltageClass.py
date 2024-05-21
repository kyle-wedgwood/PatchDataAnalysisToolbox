import matplotlib.pyplot as plt
from SeriesClass import Series

class ContinuousVoltage( Series):
    '''Class for voltage clamp analysis'''

    def __init__( self, exp_object, obj, index):
        '''Initialiser for voltage clamp class'''

        super( ContinuousVoltage, self).__init__( exp_object, obj, index)


    def plot_stimuli_and_responses( self, protocol='all', folder_name='.'):
        '''Plot responses'''

        if (protocol == 'all' or protocol == self.name):
            y_label = 'Current (pA)'

            plt.rcParams.update({'font.size': 22})
            fig, ax = plt.subplots( figsize=(24,8))
            ax.set_xlabel( 'Time (%s)' % self.t_unit)
            ax.set_ylabel( y_label)

            plt.plot( self.time, 1e12*self.data['I-mon'], lw=2)
            ax.set_xlim( [self.time[0], self.time[-1]])

            plot_pars = {}

            fig_filename = self.post_process_figure( fig, ax, plot_pars, \
                    folder_name, 'stimulus_response')

            return fig_filename



