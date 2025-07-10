import datetime
import numpy as np

class Base( object):
    '''Base object for all Symphony groups'''

    def __init__( self, parent, uuid, pars, count=0):
        '''Initialiser for general class'''
        self.id = uuid
        self.parent = parent
        self.load_pars( pars)
        self.child_list = []
        self.no = count # Note that this may be later overridden

        self.set_start_time()
        self.name = self.decode_byte_string(self.group.attrs.get('label'))

        properties_group = self.group.get('properties')
        if properties_group:
            properties = properties_group.attrs

            for prop_pair in properties.items():
                setattr(self, prop_pair[0], prop_pair[1])

        notes = self.group.get('notes')
        if notes:
            self.notes = notes[:] # colon operator needed to load notes into array
        else:
            self.notes = None


    def __getitem__( self, attr):
        '''Returns attribute of class object'''
        return getattr( self, attr)


    def create_dict( par_array):
        '''Create dictionary from parameter array'''
        par_dict = {}

        for pair in par_array.items():
            par_dict[pair[0]] = pair[1]

        return par_dict


    def load_pars( self, par_list):
        '''Copies attributes from group to class object'''
        for par_pair in par_list.items():
            setattr( self, par_pair[0], par_pair[1])


    def check_attr( self, attr, par_array):
        '''Check if attribute exists in par array and returns value'''
        if attr in par_array.keys():
            return par_array.get( attr)
        else:
            return None


    def fetch_list( self):
        '''Return list of children'''
        return self.child_list


    def add_child( self, klass, uuid, counter):
        print(self)
        '''Creates and add child instance to child_list'''
        self.child_list.append( klass( self, uuid, counter))


    def populate_list( self, child_list, klass):
        '''Populate the child list with instances of specified class'''
        for counter, uuid in enumerate( child_list):
            self.add_child( klass, uuid, counter)


        self.reorder_child_list()


    def reorder_child_list( self):
        '''Reorder list of children according to their creation time'''
        start_times = []
        for child in self.child_list:
            start_times.append( child.start_time)

        # Renumber according to ordered list
        self.child_list = [ child for _, child in sorted( zip( start_times, self.child_list))]
        for no, child in enumerate( self.child_list):
            child.no = no


    def set_start_time( self):
        '''Get start time of group'''
        ticks = self.group.attrs.get( 'startTimeDotNetDateTimeOffsetTicks', None)
        if not ticks:
            ticks = self.group.attrs.get( 'creationTimeDotNetDateTimeOffsetTicks', None)

        self.start_time = self.convert_time( ticks)


    @staticmethod
    def convert_time( ticks):
        '''Converts .NET ticks to python datetime'''
        return datetime.datetime(1, 1, 1) + datetime.timedelta(microseconds = ticks/10)


    @staticmethod
    def decode_byte_string(var):
        '''Converts byte string to unicode string'''
        if isinstance(var, bytes):
            var = var.decode()

        return var


    def plot_stimuli( self, protocol='all', named_pars=[], folder_name=None):
        '''Calls children's plot_stimuli function until a child overloads it'''
        for child in self.child_list:
            child.plot_stimuli( protocol, named_pars, folder_name)


    def plot_responses( self, protocol='all', named_pars=[], folder_name=None):
        '''Calls children's plot_responses function until a child overloads it'''
        for child in self.child_list:
            child.plot_responses( protocol, named_pars, folder_name)


    def fetch_plot_pars( self, plot_pars, named_pars):
        '''Searches up tree to find parameters and store in dict'''
        pars_to_find = list( named_pars)
        for par in pars_to_find:
            val = getattr( self, par, None)
            if val is not None:
                plot_pars[par] = val
                pars_to_find.remove( par)


        if ( pars_to_find and getattr( self, 'parent', None)):
            self.parent.fetch_plot_pars( plot_pars, pars_to_find)


        return plot_pars


    def make_plot( self, function_name, **kwargs):
        '''Searches root nodes for function_name and executes'''
        for child in self.child_list:
            child.make_plot( function_name, **kwargs)


    def analyse_data( self, function_name, data, include_list, **kwargs):
        '''Searches root nodes for function_name and executes'''
        for child in self.child_list:
            child.analyse_data( function_name, data, include_list, **kwargs)


    def add_notes( self, notes, pdf):
        '''Adds notes to pdf report'''
        pdf.set_font( 'arial', 'B', 12)

        pdf.cell( w=0, h=pdf.line_height, txt='', ln=1)
        pdf.cell( w=0, h=pdf.line_height, txt='Notes', ln=1)

        pdf.set_font( 'arial', 'I', 12)

        for note in notes:
            time = self.convert_time( note[0][0])
            val  = note[1]
            pdf.cell( w=20, h=pdf.line_height, txt=time.strftime( '%H:%M:%S'), ln=0)
            pdf.multi_cell(w=0, h=pdf.line_height, txt=': %s' % val.decode(), align='L')


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

        exclude_list = [ 'parent', 'group', 'child_list', 'no', 'start_time', 'notes', 'name']

        for key, val in sorted( self.__dict__.items()):
            if isinstance(val, bytes):
                val = val.decode()

            if not key in exclude_list:
                pdf.cell( w=max( [string_width, pdf.line_width]), h=pdf.line_height, txt=key, ln=0)
                pdf.multi_cell(w=0, h=pdf.line_height, txt=': %s' % val, align='L')


        # Add notes if they are present
        if self.notes is not None:
            self.add_notes(self.notes, pdf)

        for child in self.child_list:
            child.make_pdf_report( pdf)


    def save_data_ascii( self):
        '''Loops over datasets and writes them to a text file'''
        for child in self.child_list:
            child.save_data_ascii()


    def check_tag( self, tag_name, val, exclude_list):
        '''Loops over children and checks for tags'''
        for child in self.child_list:
            child.check_tag( tag_name, val, exclude_list)


        return exclude_list


    def fetch_protocol_uuids( self, protocol_uuids, exclude_repeats=True, exclude_list=[]):
        '''Fetches uuids of protcols associated with object'''
        for child in self.child_list:
            child.fetch_protocol_uuids( protocol_uuids, exclude_repeats, exclude_list)


    def check_tag_value( self, tag_name, val, exclude_list):
        '''Checks tag value and excludes protocol uuid if necessary'''
        for key in self.__dict__.keys():
            if tag_name in key.upper():
                try:
                    if ( self[key].upper() != val.upper()):
                        self.fetch_protocol_uuids( exclude_list, exclude_repeats=False)
                        break
                except: # Remove protocols if we can't decide whether they should be included
                    self.fetch_protocol_uuids( exclude_list, exclude_repeats=False)
                    break


    def fetch_object_by_uuid( self, uuid):
        '''Returns object associated to specific uuid'''
        obj = None
        if ( self.id == uuid):
            return self

        else:
            for child in self.child_list:
                obj = child.fetch_object_by_uuid( uuid)
                if obj is not None:
                    return obj

            return obj


    @staticmethod
    def compute_reversal_potential( temp, valence, int_conc, ext_conc):
        '''Compute reversal potential according to Nernst equation'''

        tempKelvin = temp + 273.15
        R = 8.314
        F = 96485

        return 1000*R*tempKelvin/(valence*F)*np.log( ext_conc/int_conc);


    @staticmethod
    def BoltzmannFunction( x, V):
        '''Boltzmann residual function for fitting'''
        return 1.0/( 1.0+np.exp( -(V-x[0])/x[1]))


    @staticmethod
    def NegExponential( a, x):
        '''Monoexponential for fitting recovery'''
        return a[0]*( 1.0-np.exp( a[1]*x))


    @staticmethod
    def Exponential( a, x):
        '''Monoexponential for fitting recovery'''
        return a[0]*np.exp( a[1]*x)


    @staticmethod
    def BiExponential( x, a1, b1, a2, b2, c):
        '''Biexponential with offset for curve fitting'''
        return a1*np.exp( -x/b1) + a2*np.exp( -x/b2) + c


    @staticmethod
    def OffsetExponential( x, a, b, c):
        '''Monoexponential with offset for curve fitting'''
        return a*np.exp( -x/b) + c

    @staticmethod
    def Linear( x, a, b):
        '''Liner function for curve fitting'''
        return x*a + b
