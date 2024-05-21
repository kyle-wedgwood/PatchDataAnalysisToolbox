import matplotlib.pyplot as plt
from SeriesClass import Series

class Ramp( Series):
    '''Class for GapFree analysis'''

    def __init__( self, exp_object, obj, index):
        '''Initialiser for GapFree class'''

        super( Ramp, self).__init__( exp_object, obj, index)


    def plot_stimulus( self, ax):
        '''Plot stimulus'''
        ax.plot( self.time, self.data[self.stim_channel], lw=2, color='black')


    def plot_response( self, ax):
        '''Plot response'''
        ax.plot( self.time, self.data[self.resp_channel], lw=2, color='black')


