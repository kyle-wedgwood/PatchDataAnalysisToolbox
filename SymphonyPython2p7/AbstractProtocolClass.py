import abc
import os
import CellClass
import PreparationClass
import re
import numpy as np
from BaseClass import Base
from EpochClass import Epoch
from matplotlib import pyplot as plt

class AbstractProtocol( Base):
    __metaclass__ = abc.ABCMeta
    '''This class defines an object to interact with Symphony files'''

    def __init__( self, epoch_group_object, block_uuid, count):
        '''Initialiser for abstract EpochBlock'''

        blocks_group = epoch_group_object.group.get( 'epochBlocks')
        self.group = blocks_group.get( block_uuid)

        protocol_pars = self.group.get( 'protocolParameters').attrs

        super( AbstractProtocol, self).__init__( epoch_group_object, block_uuid, protocol_pars, count)

        self.totalTime = self.fetch_total_time()
        self.noPts = int( self['totalTime']*self['sampleRate']/1000.0)
        self.time = np.array( range( self['noPts']))/self['sampleRate']*1000.0 # time in ms
        self.holdingValue = self.fetch_holding_value()

        epoch_list = self.group.get( 'epochs').keys()
        self.populate_list( epoch_list, Epoch)
        self.load_data()

        if not epoch_list:
            self.operating_mode = 'VClamp'
            self.pdf_vars = { 'No data': 'Aborting loading'}
            return


        self.amp_prop, self.amp_name = self.fetch_amplifier_properties()
        self.operating_mode = self.amp_prop.get( 'operatingMode')
        self.bath_temperature = self.fetch_bath_temperature()
        self.membrane_capacitance = self.amp_prop['membraneCapacitance']*1e12

        # Parameters to print in pdf report
        self.pdf_vars = { 'Bath temperature (C)'  : self.bath_temperature,
                          'Filter frequency (Hz)' : self.amp_prop['lpfCutoff'],
                          'Sampling rate (Hz)'    : self['sampleRate']}

        if self.operating_mode == 'VClamp':
            series_resistance = self.amp_prop.get( 'seriesResistance', 0.0)
            self.pdf_vars.update( {'Series resistance (MOhm)': \
                    series_resistance*1e-6,
                   'Whole cell capacitance (pF)':  \
                    self.amp_prop['membraneCapacitance']*1e12})
        elif self.operating_mode == 'IClamp':
            pipCapNeut = 0.0
            if 'properties' in self.group.keys():
                properties = self.group.get( 'properties').attrs
                for key in properties.keys():
                    if 'Pipette' in key:
                        pipCapNeut = properties[key]


            self.pdf_vars.update( {'Pipette capacitance neutralisation (pF)': \
                pipCapNeut})


    @abc.abstractmethod
    def load_data( self):
        '''Loads data into array'''
        pass


    @abc.abstractmethod
    def fetch_total_time( self):
        '''Returns maximum time of protocol'''
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


    def fetch_response( self, epoch_uuid, response_name=None):
        '''Gets response data from specific epoch'''
        response_group = self.group.get( 'epochs/' + epoch_uuid + '/responses')
        uuid = response_group.visit( lambda name: self.find_string( name, 'data'))
        response_data = response_group.get( uuid)
        return response_data['quantity']


    def fetch_stimulus_pars( self, epoch_uuid):
        '''Gets stimulus parameters for specific epoch'''
        epoch_group = self.group.get( 'epochs/' + epoch_uuid)
        stim_pars = {}
        stimulus_group = epoch_group.get( 'stimuli')
        uuid = stimulus_group.visit( lambda name: self.find_string( name, 'Amp'))
        protocol_pars = stimulus_group.get( uuid + '/parameters').attrs
        for key, val in protocol_pars.items():
            stim_pars[key] = val

        # Now fetch any specific parameters
        if 'protocolParameters' in epoch_group.keys():
            protocol_pars = epoch_group.get ( 'protocolParameters').attrs
            for key, val in protocol_pars.items():
                stim_pars[key] = val


        return stim_pars


    def fetch_protocol_uuids( self, protocol_uuids, exclude_repeats, exclude_list):
        '''Adds protocol uuid to list'''
        protocol_uuids.append( self.id)


    def fetch_stimulus_properties( self, epoch_uuid):
        '''Gets stimulus properties for specific epoch'''
        return self.group.get( 'epochs/' + epoch_uuid).get( 'properties').attrs


    def fetch_amplifier_properties( self, amp=1):
        '''Gets properties of amplifier at start of protocol'''
        response_group = self.child_list[0].group.get( 'responses')
        amp_uuid = response_group.items()[amp-1][0]
        config_uuid = amp_uuid + '/dataConfigurationSpans/span_0'
        config_group = response_group.get( config_uuid)
        for item in config_group.keys():
            if 'Amp' in item:
                return config_group.get( item).attrs, item


    def fetch_bath_temperature( self):
        '''Gets the average bath temperature across the protocol recording'''
        count = 0
        bath_temperature = 0.0
        for epoch_no, epoch in enumerate( self.child_list):
            stim_prop = epoch.fetch_stimulus_properties()
            if 'bathTemperature' in stim_prop.keys():
                bath_temperature += stim_prop['bathTemperature']
                count += 1


        if count > 0:
            return bath_temperature/count
        else:
            return self.parent.parent.parent['bathTemperature']


    def fetch_holding_value( self):
        '''Fetch holding value from protocol parameters if it exists, else use
        Prep value'''
        if 'properties' in self.group.keys():
            properties = self.group.get( 'properties').attrs
            for key in properties.keys():
                if 'Holding' in key:
                    return float( properties[key])

        prep = self.parent.parent.parent
        for key in prep.__dict__.keys():
            if 'Holding' in key:
                return float( re.findall(r'-?\d+\.?\d*', str( prep[key]))[0])


        return -60.0


    def save_fig( self, fig, folder_name, string, name_type='uuid'):
        '''Saves figure to specified folder'''
        if not os.path.exists( folder_name):
            os.makedirs( folder_name)

        if name_type == 'iterative':
            cell_no = self.find_cell_no()
            fig_filename = '%s/cell_%d_group_%d_block_%d_%s_%s.png' % (folder_name, cell_no, \
                self.parent.no, self.no, self.__class__.__name__, string)

        elif name_type == 'uuid':
            uuid = self.id.split( '.')[-1]
            fig_filename = '%s/%s_%s.png' %( folder_name, uuid, string)


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
            elif (self.operating_mode == 'IClamp') \
                    or (self.operating_mode == 'I0'):
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


    def plot_responses( self, protocol='all', named_pars=[], y_lim=None, folder_name=None):
        '''Sets up figure and axis handle then calls plotting function'''
        if (protocol == 'all' or protocol == self.name):
            if self.operating_mode == 'VClamp':
                y_label = 'I (pA)'
            elif (self.operating_mode == 'IClamp') \
                    or (self.operating_mode == 'I0'):
                y_label = 'V (mV)'

            plt.rcParams.update({'font.size': 22})
            fig, ax = plt.subplots( figsize=(12,8))
            ax.set_xlabel( 'Time (ms)')
            ax.set_ylabel( y_label)

            # Now find plot parameters
            plot_pars = {}
            plot_pars = self.fetch_plot_pars( plot_pars, named_pars)

            self.plot_response( ax)

            if y_lim:
                ax.set_ylim( y_lim)

            fig_filename = self.post_process_figure( fig, ax, plot_pars, \
                    folder_name, 'response')

            return fig_filename


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

            plt.rcParams.update({'font.size': 22})
            fig, ax = plt.subplots( ncols=2, figsize=(24,8))
            ax[0].set_xlabel( 'Time (ms)')
            ax[0].set_ylabel( s_label)
            ax[1].set_xlabel( 'Time (ms)')
            ax[1].set_ylabel( r_label)

            # Now find plot parameters
            plot_pars = {}
            plot_pars = self.fetch_plot_pars( plot_pars, named_pars)

            self.plot_stimulus( ax[0])
            self.plot_response( ax[1])

            fig_filename = self.post_process_figure( fig, ax[1], plot_pars, \
                    folder_name, 'stimulus_response')

            return fig_filename


    def find_cell_no( self):
        '''Finds number of cell'''
        cell_no = None
        obj = self.parent
        while cell_no is None:
            if isinstance( obj, CellClass.Cell):
                cell_no = obj.no

            obj = obj.parent

        return cell_no


    def find_prep_no( self):
        '''Find number of preparation'''
        prep_no = None
        obj = self.parent
        while prep_no is None:
            if isinstance( obj, PreparationClass.Preparation):
                prep_no = obj.no

            obj = obj.parent

        return prep_no


    def make_plot( self, function_name, **kwargs):
        '''Evaluates plotting function if it is a class method'''
        if function_name in dir( self):
            function = 'self.' + function_name
            eval( function)(**kwargs)


    def analyse_data( self, function_name, data, include_list=[], **kwargs):
        '''Evaluates analysis function if it is a class method'''

        if (function_name in dir( self)) & (self.id in include_list):
            function = 'self.' + function_name
            eval( function)( data, **kwargs)


    def make_pdf_reports( self, pdf): # Deprecated
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
        pdf.set_font( 'arial', 'B', 24)
        pdf.write( h=3*pdf.line_height, txt=self.__class__.__name__)
        pdf.set_font( 'arial', '', 16)

        pdf.cell( w=0, h=3*pdf.line_height, align='L', txt='   %s' % self.start_time.strftime( '%H:%M:%S'), ln=1)

        pdf.set_font( 'arial', '', 12)
        string_width = pdf.get_string_width( max( self.pdf_vars.keys(), key=len))

        pdf.cell( w=0, h=pdf.line_height, txt='id: %s' % self.id, ln=1)

        for key, val in sorted( self.pdf_vars.items()):
            pdf.cell( w=max( [string_width, pdf.line_width]), h=pdf.line_height, txt=key, ln=0)
            pdf.multi_cell(w=0, h=pdf.line_height, txt=': %s' % val, align='L')

        fig_filename = self.plot_stimuli_and_responses( folder_name='.')

        pdf.image( fig_filename, w=180)

        # Cleanup
        os.remove( fig_filename)


    @staticmethod
    def create_color_map( base_cmap, N):
        '''Create colormap with N distinct levels from base map'''
        base = plt.cm.get_cmap( base_cmap)
        color_list = base( np.linspace(0, 1, N))

        return color_list


    def save_data_ascii( self, folder_name='.'):
        '''Saves stimulus and response to a text file'''
        cell_no = self.find_cell_no()
        prep_no = self.find_prep_no()

        filename = \
        '%s/prep_%d_cell_%d_group_%d_block_%d_%s_time_stimulus_response.dat' % \
        (folder_name, prep_no, cell_no, \
                self.parent.no, self.no, self.__class__.__name__)

        time = np.array( [self.time]).transpose()
        if 'stimulus' not in self.__dict__: # THIS IS A HACK 24.2.2020
            self.stimulus = np.zeros( shape=( self.response.shape[0],1))

        buf = np.nan*np.ones( shape=( self.stimulus.shape[0],1))
        data = np.concatenate( (time, buf, self.stimulus, buf, self.response), axis=1)

        np.savetxt( filename, data)


    def fetch_membrane_capacitance( self, data=None):
        '''Returns membrane capacitance'''
        val = self.membrane_capacitance
        if data is not None:
            cell_no = self.parent.parent.no
            if cell_no in data.keys():
                data[cell_no] = np.append( data[cell_no], val)
            else:
                data[cell_no] = val*np.ones( shape=(1))
