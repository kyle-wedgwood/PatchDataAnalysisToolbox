import abc
import os
import CellClass
import numpy as np
from BaseClass import Base
from matplotlib import pyplot as plt
from PIL import Image

class AbstractProtocol( Base):
    __metaclass__ = abc.ABCMeta
    '''This class defines an object to interact with Symphony files'''

    def __init__( self, epoch_group_object, block_uuid, count):
        '''Initialiser for abstract EpochBlock'''

        blocks_group = epoch_group_object.group.get( 'epochBlocks')
        self.group = blocks_group.get( block_uuid)

        protocol_pars = self.group.get( 'protocolParameters').attrs

        super( AbstractProtocol, self).__init__( epoch_group_object, block_uuid, protocol_pars, count)

        self.totalTime = self['preTime'] + self['stimTime'] + self['tailTime']
        self.noPts = int( self['totalTime']*self['sampleRate']/1000.0)
        self.holding_potential = -60.0
        self.child_list = self.group.get( 'epochs')
        self.time = np.array( range( self['noPts']))/self['sampleRate']*1000.0 # time in ms
        self.operating_mode = self.group.visititems( lambda name, obj: self.find_attribute( name, obj, 'operatingMode'))
        self.load_data()


    @abc.abstractmethod
    def load_data( self):
        '''Loads data into array'''
        pass


    @staticmethod
    def find_string( name, string):
        '''Return name if it contains string'''
        if string in name:
            return name


    @staticmethod
    def find_attribute( name, obj, attr):
        '''Return name if it has attribute'''
        if attr in obj.attrs.keys():
            return obj.attrs.get( attr)


    def fetch_response( self, epoch_uuid):
        '''Gets response data from epoch'''
        response_group = self.child_list.get( epoch_uuid + '/responses')
        uuid = response_group.visit( lambda name: self.find_string( name, 'data'))
        response_data = response_group.get( uuid)
        return response_data['quantity']


    def fetch_stimulus_pars( self, epoch_uuid):
        '''Gets stimulus parameters for specific epoch'''
        stimulus_group = self.child_list.get( epoch_uuid + '/stimuli')
        uuid = stimulus_group.visit( lambda name: self.find_string( name, 'Amp'))
        return stimulus_group.get( uuid + '/parameters').attrs


    def save_fig( self, fig, folder_name, string):
        '''Saves figure to specified folder'''
        if not os.path.exists( folder_name):
            os.makedirs( folder_name)

        cell_no = self.find_cell_no()

        fig_filename = '%s/cell_%d_block_%d_%s_%s.png' % (folder_name, cell_no, \
                self.no, self.__class__.__name__, string)
        fig.savefig( fig_filename, bbox_inches='tight')

        return fig_filename


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


    @abc.abstractmethod
    def plot_stimulus( self, ax):
        pass


    @abc.abstractmethod
    def plot_response( self, ax):
        pass


    def plot_stimuli( self, protocol='all', named_pars=[], folder_name=None):
        '''Sets up figure and axis handle then calls plotting function'''
        if (protocol == 'all' or protocol == self.name):
            if self.operating_mode == 'VClamp':
                y_label = 'V (mV)'
            elif self.operating_mode == 'IClamp':
                y_label = 'I (pA)'

            plt.rcParams.update({'font.size': 22})
            fig, ax = plt.subplots( figsize=(12,8))
            ax.set_xlabel( 'Time (ms)')
            ax.set_ylabel( y_label)

            # Now find plot parameters
            plot_pars = {}
            plot_pars = self.fetch_plot_pars( plot_pars, named_pars)

            self.plot_stimulus( ax)

            fig_filename = self.post_process_figure( fig, ax, plot_pars, \
                    folder_name, 'stimulus')

            return fig_filename


    def plot_responses( self, protocol='all', named_pars=[], folder_name=None):
        '''Sets up figure and axis handle then calls plotting function'''
        if (protocol == 'all' or protocol == self.name):
            if self.operating_mode == 'VClamp':
                y_label = 'I (pA)'
            elif self.operating_mode == 'IClamp':
                y_label = 'V (mV)'

            plt.rcParams.update({'font.size': 22})
            fig, ax = plt.subplots( figsize=(12,8))
            ax.set_xlabel( 'Time (ms)')
            ax.set_ylabel( y_label)

            # Now find plot parameters
            plot_pars = {}
            plot_pars = self.fetch_plot_pars( plot_pars, named_pars)

            self.plot_response( ax)

            fig_filename = self.post_process_figure( fig, ax, plot_pars, \
                    folder_name, 'response')

            return fig_filename


    def find_cell_no( self):
        cell_no = None
        obj = self.parent
        while cell_no is None:
            if isinstance( obj, CellClass.Cell):
                cell_no = obj.no

            obj = obj.parent

        return cell_no


    def make_plot( self, function_name, **kwargs):
        '''Evaluates plotting function if it is a class method'''
        if function_name in dir( self):
            function = 'self.' + function_name
            eval( function)(**kwargs)


    def analyse_data( self, function_name, **kwargs):
        '''Evaluates analysis function if it is a class method'''
        if function_name in dir( self):
            function = 'self.' + function_name
            eval( function)(**kwargs)


    def make_pdf_reports( self, pdf):
        '''Add stimulus and response figures to pdf report'''
        pass
        pdf.set_font( 'arial', 'B', 24)
        pdf.write( h=3*pdf.line_height, txt=self.__class__.__name__)
        pdf.set_font( 'arial', '', 16)

        pdf.cell( w=0, h=3*pdf.line_height, align='L', txt='   %s' % self.start_time.strftime( '%H:%M:%S'), ln=1)

        start_x = pdf.get_x()
        start_y = pdf.get_y()
        im_width = 90

        fig_filename = self.plot_stimuli( folder_name='.')
        pdf.image( fig_filename, x=start_x, y=start_y, w=im_width)
        os.remove( fig_filename)

        pdf.set_xy( start_x + im_width + 2, start_y)

        fig_filename = self.plot_responses( folder_name='.')
        pdf.image( fig_filename, x=pdf.get_x(), y=pdf.get_y(), w=im_width)
        os.remove( fig_filename)

        pdf.cell( w=0, h=60, ln=1)


    def make_pdf_report( self, pdf):
        '''Add stimulus and response figures to pdf report'''
        pass
        pdf.set_font( 'arial', 'B', 24)
        pdf.write( h=3*pdf.line_height, txt=self.__class__.__name__)
        pdf.set_font( 'arial', '', 16)

        pdf.cell( w=0, h=3*pdf.line_height, align='L', txt='   %s' % self.start_time.strftime( '%H:%M:%S'), ln=1)

        stimulus_filename = self.plot_stimuli( folder_name='.')
        response_filename = self.plot_responses( folder_name='.')

        images = map(Image.open, [ stimulus_filename, response_filename])
        widths, heights = zip(*(i.size for i in images))

        total_width = sum( widths)
        max_height  = max( heights)

        new_im = Image.new( 'RGB', (total_width, max_height))

        x_offset = 0
        for im in images:
            new_im.paste(im, (x_offset,0))
            x_offset += im.size[0]


        new_im.save( stimulus_filename)

        pdf.image( stimulus_filename, w=180)

        # Cleanup
        os.remove( stimulus_filename)
        os.remove( response_filename)


