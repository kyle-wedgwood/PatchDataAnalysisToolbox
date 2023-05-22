import h5py
import numpy as np
from BaseClass import Base
from SubjectClass import Subject
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from scipy.optimize import minimize

class Experiment( Base):
    '''Class to store data for whole recording session'''

    def __init__( self, filename):
        '''Initialiser for experiment class'''

        self.filename = filename

        file_id = h5py.File( filename, 'r')

        exp_uuid = list(file_id.items())[-1][0]
        self.group = file_id.get( exp_uuid)

        self.purpose = self.group.attrs['purpose']
        exp_pars = self.group.get( 'properties').attrs

#        end_time = self.convert_time( self.group.attrs.get( 'endTimeDotNetDateTimeOffsetTicks'))
#        setattr( self, 'end time (24 hr)', end_time.strftime( '%H:%M:%S'))
#        setattr( self, 'date', end_time.strftime( '%a %d %b %Y'))

        super( Experiment, self).__init__( None, exp_uuid, exp_pars)

        subj_list = self.group.get( 'sources/').keys()
        self.populate_list( subj_list, Subject)

        file_id.close() # Close file once data have been loaded


    def make_pdf_report( self):
        '''Produces a PDF report with notes and data plotted'''
        from fpdf import FPDF
        pdf = FPDF()
        pdf.line_height = 5
        pdf.line_width  = 40
        pdf.set_top_margin( 10.0)
        pdf.set_left_margin( 10.0)
        pdf.add_page()

        super( Experiment, self).make_pdf_report( pdf)
        filename = self.filename + '_report.pdf'
        pdf.output( filename, 'F')


    # CONSIDER REMOVING FROM HERE DOWNWARDS
    def compute_mean_IV_curve( self, folder_name=None, **kwargs):
        '''Computes IV curve averaged over cells'''

        data = {}
        self.analyse_data( 'compute_normalised_current', data, **kwargs)

        grouped_data = self.group_data( data)

        fig, ax = self.plot_analysed_results( grouped_data)

        ax.set_xlabel( 'Membrane potential (mV)')
        ax.set_ylabel( 'Current (pA/pF)')

        ax.axhline( y=0, color='grey', lw=4, ls='--')

        if folder_name:
            fig.savefig( self.filename + '_averaged_IV_curve.png', bbox_inches='tight')


    def compute_peak_IV_curve( self, folder_name=None, **kwargs):
        '''Computes IV curve averaged over cells'''

        data = {}
        self.analyse_data( 'compute_normalised_peak_current', data, **kwargs)

        grouped_data = self.group_data( data)

        fig, ax = self.plot_analysed_results( grouped_data)

        ax.set_xlabel( 'Membrane potential (mV)')
        ax.set_ylabel( 'Peak Current (pA/pF)')

        ax.axhline( y=0, color='grey', lw=4, ls='--')

        if folder_name:
            fig.savefig( self.filename + '_averaged_peak_IV_curve.png', bbox_inches='tight')


    def compute_activation_curve( self, folder_name=None, **kwargs):
        '''Compute steady state activation curve'''

        data = {}
        self.analyse_data( 'compute_normalised_conductance', data, **kwargs)

        grouped_data = self.group_data( data, normalise=True)

        fig, ax = self.plot_analysed_results( grouped_data)

        ax.set_xlabel( 'Membrane potential (mV)')
        ax.set_ylabel( '$G/G_{max}$')

        ax.axhline( y=0, color='grey', lw=4, ls='--')

        # Perform fit to activation
        fun = lambda x : np.sum( \
            ( self.BoltzmannFunction( x, grouped_data['stim']) - grouped_data['mean'])**2)
        res = minimize( fun, x0=[-10,5])

        stimulus_fine = np.arange( start=grouped_data['stim'][0],\
                                   stop=grouped_data['stim'][-1], step=0.01)

        ax.plot( stimulus_fine, self.BoltzmannFunction( res.x, stimulus_fine), \
                color='red', lw=4, dash_capstyle='round')

        if folder_name:
            fig.savefig( self.filename + '_activation_curve.png', bbox_inches='tight')

        grouped_data['V_half'] = res.x[0]
        grouped_data['k']      = res.x[1]

        return grouped_data, ax


    def compute_inactivation_curve( self, folder_name=None, **kwargs):
        '''Compute steady state inactivation curve'''

        data = {}
        self.analyse_data( 'compute_normalised_peak_inactivation_current', data, **kwargs)

        grouped_data = self.group_data( data, normalise=True)

        fig, ax = self.plot_analysed_results( grouped_data)

        ax.set_xlabel( 'Membrane potential (mV)')
        ax.set_ylabel( '$I/I_{max}$')

        # Perform fit to activation
        fun = lambda x : np.sum( ( \
            self.BoltzmannFunction( x, grouped_data['stim']) - grouped_data['mean'])**2)
        res = minimize( fun, x0=[-10,-5])

        stimulus_fine = np.arange( start=grouped_data['stim'][0],\
                                   stop=grouped_data['stim'][-1], step=0.01)

        ax.plot( stimulus_fine, self.BoltzmannFunction( res.x, stimulus_fine), \
                color='red', lw=4, dash_capstyle='round')

        if folder_name:
            fig.savefig( self.filename + '_inactivation_curve.png', bbox_inches='tight')

        grouped_data['V_half'] = res.x[0]
        grouped_data['k']      = res.x[1]

        return grouped_data, ax


    def compute_inactivation_recovery( self, folder_name=None, **kwargs):
        '''Compute fast recovery times from inactivation'''
        data = {}
        self.analyse_data( 'compute_peak_current_ratio_fast', data, **kwargs)

        grouped_data = self.group_data( data, normalise=True)

        fig, ax = self.plot_analysed_results( grouped_data)

        ax.set_xlabel( 'Pulse interval(ms)')
        ax.set_ylabel( 'Current ratio')

        ax.axhline( y=1, color='grey', lw=4, ls='--')

        # Perform fit to recovery times
        fun = lambda x : np.sum( (\
            self.NegExponential( x, grouped_data['stim']) - grouped_data['mean'])**2)
        res = minimize( fun, x0=[1,-0.2])

        interval_fine = np.arange( start=grouped_data['stim'][0],\
                                   stop=grouped_data['stim'][-1], step=0.01)

        ax.plot( interval_fine, self.NegExponential( res.x, interval_fine), \
                color='red', lw=4, dash_capstyle='round')

        if folder_name:
            fig.savefig( self.filename + '_inactivation_recovery_curve.png', bbox_inches='tight')


        grouped_data['recovery_fast'] = res.x[1]

        return grouped_data, ax


    def compute_slow_inactivation_recovery( self, folder_name=None, **kwargs):
        '''Compute fast recovery times from inactivation'''
        data = {}
        self.analyse_data( 'compute_peak_current_ratio_slow', data, **kwargs)

        grouped_data = self.group_data( data, normalise=True)

        fig, ax = self.plot_analysed_results( grouped_data)

        ax.set_xlabel( 'Pulse duration (ms)')
        ax.set_ylabel( 'Current ratio')

        ax.axhline( y=1, color='grey', lw=4, ls='--')

        # Perform fit to recovery times
        fun = lambda x : np.sum( \
            ( self.Exponential( x, grouped_data['stim']) - grouped_data['mean'])**2)
        res = minimize( fun, x0=[0.8,-0.0002])

        duration_fine = np.arange( start=grouped_data['stim'][0],\
                                   stop=grouped_data['stim'][-1], step=0.01)

        ax.plot( duration_fine, self.Exponential( res.x, duration_fine), \
                color='red', lw=4, dash_capstyle='round')

        if folder_name:
            fig.savefig( self.filename + '_slow_inactivation_recovery_curve.png', bbox_inches='tight')


        grouped_data['recovery_slow'] = res.x[1]

        return grouped_data, ax


    def compute_whole_cell_conductance( self, folder_name=None, **kwargs):
        '''Compute whole cell conductance averaged over cells'''

        data = { 'conductance': []}
        self.analyse_data( 'compute_whole_cell_conductance', data, **kwargs)

        # Plot bar chart of results
        fig, ax = plt.subplots( figsize=(12,8))

        ax.set_ylabel( 'Conductance (nS/pF)')

        ax.boxplot( data['conductance'])

        if folder_name:
            fig.savefig( self.filename + '_averaged_conductance.png', bbox_inches='tight')


        return ax


    def compute_maximal_conductance( self, folder_name=None, **kwargs):
        '''Compute maximal condutance for given inward/outward channel'''
        data = {}
        self.analyse_data( 'compute_normalised_conductance', data, **kwargs)

        grouped_data = self.group_data( data)

        max_conductance_ind = np.argmax( np.abs( grouped_data['mean']))
        stim_val = grouped_data['stim'][max_conductance_ind]

        # Plot bar chart of results
        fig, ax = plt.subplots( figsize=(12,8))

        ax.set_ylabel( 'Maximal conductance (nS/pF)')

        ax.boxplot( data[stim_val])

        if folder_name:
            fig.savefig( self.filename + '_maximal_conductance.png', bbox_inches='tight')


        return ax


    def compute_gap_junction_conductance( self, folder_name=None, **kwargs):
        '''Compute gap junction conductance over all cells'''
        data = {}
        self.analyse_data( 'compute_gap_junction_conductance', data, **kwargs)

        grouped_data = self.group_data( data)

        fig, ax = self.plot_analysed_results( grouped_data)

        ax.set_xlabel( 'Transjunctional potential (mV)')
        ax.set_ylabel( 'Conductance (nS/pF)')

        ax.axhline( y=0, color='grey', lw=4, ls='--')


    def group_data( self, data, normalise=False):
        '''Returns data from analysis functions'''
        stimulus = np.zeros( shape=( len(data)))
        mean_response = np.zeros( shape=( len( data)))
        std_response = np.zeros( shape=( len(data)))
        sem_response = np.zeros( shape=( len(data)))

        for pulse_no, (key, val) in enumerate( data.items()):
            no_responses = np.count_nonzero(~np.isnan(val))
            stimulus[pulse_no] = key
            mean_response[pulse_no] = np.nanmean( val)
            std_response[pulse_no] = np.nanstd( val)
            sem_response[pulse_no] = std_response[pulse_no]/np.sqrt( no_responses)


        # Reorder arrays based on stimulus amplitude
        sort_ind = np.argsort( stimulus)

        stimulus = stimulus[sort_ind]
        mean_response = mean_response[sort_ind]
        std_response = std_response[sort_ind]
        sem_response = sem_response[sort_ind]

        # Normalise if needed
        if normalise:
            mean_response /= np.max( np.abs( mean_response))

        grouped_data = { 'stim': stimulus,
                         'mean': mean_response,
                         'std' : std_response,
                         'sem' : sem_response}

        return grouped_data


    def plot_analysed_results( self, grouped_data, ax=None):
        '''Plots resutlts on axis if specified'''
        if not ax:
            fig, ax = plt.subplots( figsize=(12,8))


        ax.plot( grouped_data['stim'], grouped_data['mean'], \
                color='black', lw=4, dash_capstyle='round')
        ax.errorbar( grouped_data['stim'], grouped_data['mean'],\
                grouped_data['sem'], color='black', capsize=10)

        return fig, ax


    def merge_plots( self, ax_list, labels, filename=None):
        '''Merges two plots onto same axis'''

        fig, ax_new = plt.subplots( figsize=(12,8))
        color_flag = False

        for ax in ax_list:
            for line in ax.lines:
                color = line.get_color()
                if color_flag & (color == 'red'):
                    color = 'blue'

                if color == 'red':
                    color_flag = True


                new_line = ax_new.plot( line.get_xdata(), line.get_ydata(),
                      color=color, lw=line.get_lw())

                if (color == 'red'):
                    new_line[0].set_label( labels[0])

                elif (color == 'blue'):
                    new_line[0].set_label( labels[1])


        ax_new.set_xlabel( ax_list[0].get_xlabel())
        ax_new.set_ylabel( ax_list[0].get_ylabel())
        ax_new.legend()

        if filename:
            fig.savefig( self.filename + '_' + filename, bbox_inches='tight')


        return ax

