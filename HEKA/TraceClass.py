import numpy as np
from BaseClass import Base

class Trace( Base):
    '''Class to store trace data'''

    def __init__( self, series_object, trace, count):
        '''Initialiser for trace class'''

        super( Trace, self).__init__( series_object, trace, count)

        # Now load the actual data - this is a bit messy
        self.load_data( trace)


    def load_data( self, trace):
        '''Loads data and various associated parameters'''

        data = self.parent.parent.parent.data
        series_ind = self.parent.parent.no
        sweep_ind  = self.parent.no

        index = [ 0, series_ind, sweep_ind, self.no]
        self.data = data[index]

        self.channel = trace.Label
        self.t_unit  = trace.XUnit
        self.y_unit  = trace.YUnit
        self.dt      = trace.XInterval
        if trace.RecordingMode == '\x03':
            self.recording_mode = 'VClamp'
        elif trace.RecordingMode == '\x04':
            self.recording_mode = 'IClamp'
        elif trace.RecordingMode == '\x06':
            self.recording_mode = 'IClamp'

        self.no_data_points = trace.DataPoints
        self.time = np.array( range( self.no_data_points))*self.dt


