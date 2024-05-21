import os
import numpy as np
from BaseClass import Base

class Series( Base):
    '''Class to series data'''

    def __init__( self, exp_object, series, count):
        '''Initialiser for series class'''

        super( Series, self).__init__( exp_object, series, count)

        self.fetch_amp_prop( series)
        self.fetch_recording_mode()
        self.load_data()
        self.pdf_vars = {'GSeries': self.amp_prop['GSeries']}


    def load_data( self):
        '''Load data into an array'''

        first_trace = self.child_list[0][0]

        no_data_points = first_trace.no_data_points
        no_sweeps = self.obj.NumberSweeps
        self.t_unit = first_trace.t_unit

        channels = self.fetch_channels()
        data = {}

        for channel in channels:
            data[channel] = np.zeros( shape=(no_data_points, no_sweeps))


        for sweep_no in range( no_sweeps):
            for channel in channels:
                data[channel][:,sweep_no] = self.fetch_data( sweep_no, channel)


        self.time = self.child_list[0][0].time
        self.data = data


    def fetch_amp_prop( self, series):
        '''Load amplifier properties into dictionary'''
        self.amp_prop = {}

        for key, val in series.AmplifierState.__dict__.items():
            self.amp_prop[key] = val


    def fetch_channels( self):
        '''Gets names of active channels'''
        channels = []
        sweep = self.child_list[0]

        for trace in sweep.child_list:
            channels.append( trace.channel)

        return channels


    def fetch_data( self, sweep_no, channel):
        '''Get data from trace object for specified sweep and channel'''
        sweep = self.child_list[sweep_no]
        for trace in sweep:
            if trace.channel == channel:
                return trace.data


    def fetch_recording_mode( self):
        '''Get recording mode from a trace'''
        self.recording_mode = self.child_list[0][0].recording_mode


    def post_process_figure( self, fig, ax, plot_pars, folder_name, string):
        '''Adds title to figure and saves'''
        self.add_title( ax, plot_pars)

        if folder_name:
            fig_filename = self.save_fig( fig, folder_name, string)


        return fig_filename


    @staticmethod
    def add_title( ax, plot_pars):
        string = ''
        values = ()
        for key, val in plot_pars.items():
            string += key + ': %s, '
            values = values + (val,)

        string = string[:-2]
        ax.set_title( string % values) # Alternatively, place legend


    def save_fig( self, fig, folder_name, string):
        '''Saves figure to specified folder'''
        if not os.path.exists( folder_name):
            os.makedirs( folder_name)

        fig_filename = '%s/series_%d_%s_%s.png' % (folder_name, self.no, \
                self.name, string)
        fig.savefig( fig_filename, bbox_inches='tight')

        return fig_filename


    def make_pdf_report( self, pdf):
        '''Add stimulus and response figures to pdf report'''
        pdf.set_font( 'arial', 'B', 24)
        pdf.write( h=3*pdf.line_height, txt=self.name)
        pdf.set_font( 'arial', '', 16)

        pdf.cell( w=0, h=3*pdf.line_height, align='L', txt='   %s' % self.start_time.strftime( '%H:%M:%S'), ln=1)

        pdf.set_font( 'arial', '', 12)

        string_width = pdf.get_string_width( max( self.pdf_vars.keys(), key=len))

        for key, val in sorted( self.pdf_vars.items()):
            pdf.cell( w=max( [string_width, pdf.line_width]), h=pdf.line_height, txt=key, ln=0)
            pdf.multi_cell(w=0, h=pdf.line_height, txt=': %s' % val, align='L')


        fig_filename = '%s/series_%d_%s_%s.png' % ( self.parent.foldername, self.no, \
                self.name, 'stimulus_response')

        if os.path.exists( fig_filename):
            pdf.image( fig_filename, w=200)
        else:
            self.plot_stimuli_and_responses( folder_name=self.parent.foldername)
            pdf.image( fig_filename, w=180)

        # Cleanup
        os.remove( fig_filename)


