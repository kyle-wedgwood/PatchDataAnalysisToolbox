from BaseClass import Base

class Sweep( Base):
    '''Class to store sweep data'''

    def __init__( self, series_object, sweep, count):
        '''Initialiser for sweep class'''

        super( Sweep, self).__init__( series_object, sweep, count)
