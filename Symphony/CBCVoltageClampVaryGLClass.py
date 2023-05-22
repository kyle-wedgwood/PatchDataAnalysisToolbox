import numpy as np
from matplotlib import pyplot as plt
from matplotlib import cm as cm
from AbstractProtocolClass import AbstractProtocol

class CBCVoltageClampVaryGL(AbstractProtocol):
    '''Class for CBCVoltageClamp analysis'''

    def __init__(self, epoch_group_object, block_uuid, count):
        super(CBCVoltageClampVaryGL, self).__init__(epoch_group_object, block_uuid, count)
        self.name = 'CBCVoltageClampVaryGL'


    def load_data(self):
        '''Load data into array'''
        response = []
        stimulus = []
        gL_array = []

        for epoch_no, epoch in enumerate(self.child_list):
            stim_pars = epoch.fetch_stimulus_pars()
            stim_prop = epoch.fetch_stimulus_properties()

            if stim_prop.get('state') == 2:
                gL = stim_pars['gLeak']
                if gL in gL_array:
                    ind = gL_array.index(gL)

                else:
                    ind = len(gL_array)
                    response.append(np.zeros(0))
                    stimulus.append(np.zeros(0))
                    gL_array.append(gL)


                temp_response = epoch.fetch_response()
                stimulus[ind] = np.append(stimulus[ind], stim_pars['bifCurrent'])
                response[ind] = np.append(response[ind], np.mean(temp_response))


        # Save back to class
        self.response = response
        self.stimulus = stimulus
        self.gL_array = gL_array


    def fetch_total_time(self):
        '''Returns maximum time of protocol'''
        return 1000.0


    def plot_stimulus( self, ax):
        '''Required to overload base class function'''
        pass


    def plot_response( self, ax):
        '''Required to overload base class function'''
        pass


    def plot_stimuli_and_responses( self, protocol='all', named_pars=[], folder_name=None):
        '''Sets up figure and axis handle then calls plotting function'''
        if (protocol == 'all' or protocol == self.name):

            # Now find plot parameters
            plot_pars = {}
            plot_pars = self.fetch_plot_pars(plot_pars, named_pars)

            plt.rcParams.update({'font.size': 22})

            no_rows = int((len(self.gL_array)+1)/2)
            fig, ax = plt.subplots(no_rows, 2, figsize=(24,no_rows*8))

            ax[-1,1].set_xlabel('Current (pA)')
            ax[-1,1].set_ylabel('Voltage (mV)')

            x_lim = (np.infty, -np.infty)
            y_lim = (np.infty, -np.infty)

            # Define colormap
            for ind in range(len(self.gL_array)):
                i = int(np.floor(ind/2))
                j = np.mod(ind, 2)

                ax[i,j].set_xlabel('Current (pA)')
                ax[i,j].set_ylabel('Voltage (mV)')

                ax[i,j].plot(self.stimulus[ind], self.response[ind], linestyle='None', \
                    marker='.', markersize=20, color=cm.Set1(ind), \
                    label=('g_leak = %0.2f' % self.gL_array[ind]))

                ax[i,j].legend()

                temp_x_lim = ax[i,j].get_xlim()
                x_lim = (np.min([x_lim[0], temp_x_lim[0]]), \
                         np.max([x_lim[1], temp_x_lim[1]]))
                temp_y_lim = ax[i,j].get_ylim()
                y_lim = (np.min([y_lim[0], temp_y_lim[0]]), \
                         np.max([y_lim[1], temp_y_lim[1]]))

                ax[-1,1].plot(self.stimulus[ind], self.response[ind], linestyle='None', \
                    marker='.', markersize=20, color=cm.Set1(ind), \
                    label=('g_leak = %0.2f' % self.gL_array[ind]))


            # Set axes limits for all subplots
            for a in ax.ravel():
                a.set_xlim(x_lim)
                a.set_ylim(y_lim)


            ax[-1,1].legend()

            fig_filename = self.post_process_figure(fig, ax, plot_pars, \
                 folder_name, 'stimulus_response')

            return fig_filename
