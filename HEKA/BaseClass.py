import os
import datetime
import heka_reader
import matplotlib.pyplot as plt
import numpy as np

class Base( object):
    '''Base class for all objects'''

    def __init__( self, parent_obj, obj, count):
        '''Initialiser for Base class'''

        self.parent = parent_obj
        self.obj    = obj
        self.no     = count
        self.name   = obj.Label
        self.pdf_vars = {}

        self.child_list = []

        if 'Time' in self.obj.__dict__.keys():
            self.start_time = self.convert_time( obj.Time)
        elif 'StartTime' in self.obj.__dict__.keys():
            self.start_time = self.convert_time( obj.StartTime)

        self.populate_list( obj.children)


    @staticmethod
    def convert_time( ticks):
        '''Converts .NET ticks to python datetime'''
        ticks -= 1580970496
        if ticks < 0:
            ticks += 4294967296

        ticks += 9561652096
        ticks /= (24*60*60)

        day = datetime.datetime.fromordinal(( int(ticks)) \
                +datetime.datetime( 1602, 1, 2).toordinal())
        dayfrac = datetime.timedelta( days=ticks%1) \
                -datetime.timedelta( days=366)

        return day+dayfrac


    def populate_list( self, child_list):
        '''Populate the child list with instances of specified class'''
        for counter, obj in enumerate( child_list):
            klass = self.get_class( obj)
            self.add_child( klass, obj, counter)


    def add_child( self, klass, obj, counter):
        '''Creates and add child instance to child_list'''
        self.child_list.append( klass( self, obj, counter))


    def __getitem__( self, index):
        '''Overload getitem to return child at index'''
        return self.child_list[index]


    @staticmethod
    def get_class( obj):
        '''Returns enum class type for object'''
        obj_class = type( obj)

        if obj_class == heka_reader.SeriesRecord:

            protocol_name = obj.Label
            from Protocols import protocols
            return protocols[protocol_name]

        if obj_class == heka_reader.SweepRecord:
            from SweepClass import Sweep
            return Sweep

        if obj_class == heka_reader.TraceRecord:
            from TraceClass import Trace
            return Trace


    def load_notes( self):
        '''Load notes into list'''
        file_root = self.filename.split('.')[0]
        notesfilename = file_root + '_notes.txt'

        notes = []

        if os.path.isfile( notesfilename):
            with open( notesfilename, 'r') as fid:
                for line in fid.readlines():
                    notes.append( line.split('\n')[0])


        self.notes = notes


    def add_notes( self, pdf):
        '''Adds notes to pdf report'''
        pdf.set_font( 'arial', 'B', 12)

        pdf.cell( w=0, h=pdf.line_height, txt='', ln=1)
        pdf.cell( w=0, h=pdf.line_height, txt='Notes', ln=1)

        pdf.set_font( 'arial', 'I', 12)

        for note in self.notes:
            pdf.multi_cell(w=0, h=pdf.line_height, txt='- %s' % note, align='L')


    def plot_stimuli_and_responses( self, protocol='all', folder_name='.'):
        '''Plot responses'''

        if (protocol == 'all' or protocol == self.name):
            if self.recording_mode == 'VClamp':
                r_label = 'Current (A)'
                s_label = 'Voltage (V)'
                self.stim_channel = 'V-mon'
                self.resp_channel = 'I-mon'

            elif (self.recording_mode == 'IClamp') \
                    or (self.recording_mode == 'I0'):
                r_label = 'Voltage (V)'
                s_label = 'Current (A)'
                self.stim_channel = 'I-mon'
                self.resp_channel = 'V-mon'

            plt.rcParams.update({'font.size': 22})
            fig, ax = plt.subplots( ncols=2, figsize=(24,8))
            ax[0].set_xlabel( 'Time (%s)' % self.t_unit)
            ax[0].set_ylabel( s_label)
            ax[1].set_xlabel( 'Time (%s)' % self.t_unit)
            ax[1].set_ylabel( r_label)

            self.plot_stimulus( ax[0])
            self.plot_response( ax[1])

            plot_pars = {}

            fig_filename = self.post_process_figure( fig, ax[1], plot_pars, \
                    folder_name, 'stimulus_response')

            return fig_filename


    def make_pdf_report( self, pdf):
        '''Calls each child and adds to pdf'''

        pdf.set_font( 'arial', 'B', 24)

        if self.parent and len( self.parent.child_list) > 1:
            pdf.write( h=3*pdf.line_height, txt=self.__class__.__name__ + \
                    ' %d: %s' % (self.no+1, self.name))
        else:
            pdf.write( h=3*pdf.line_height, txt=self.__class__.__name__)

        pdf.set_font( 'arial', '', 16)
        pdf.cell( w=0, h=3*pdf.line_height, align='L', txt='   %s' % self.start_time.strftime( '%H:%M:%S'))
        pdf.ln()

        pdf.set_font( 'arial', '', 12)

        string_width = pdf.get_string_width( max( self.__dict__.keys(), key=len))

        exclude_list = [ 'parent', 'child_list', 'no', 'start_time', \
                'notes', 'name', 'data', 'obj', 'pdf_vars']

        for key, val in sorted( self.__dict__.items()):
            if not key in exclude_list:
                pdf.cell( w=max( [string_width, pdf.line_width]), h=pdf.line_height, txt=key, ln=0)
                pdf.multi_cell(w=0, h=pdf.line_height, txt=': %s' % val, align='L')


        # Add notes if they are present
        if 'notes' in self.__dict__.keys():
            self.add_notes( pdf)


        for child in self.child_list:
            child.make_pdf_report( pdf)


    @staticmethod
    def create_color_map( base_cmap, N):
        '''Create colormap with N distinct levels from base map'''
        base = plt.cm.get_cmap( base_cmap)
        color_list = base( np.linspace(0, 1, N))

        return color_list


