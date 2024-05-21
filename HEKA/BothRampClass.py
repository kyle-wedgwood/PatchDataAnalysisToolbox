import matplotlib.pyplot as plt
from SeriesClass import Series

class BothRamp( Series):
    '''Class for GapFree analysis'''

    def __init__( self, exp_object, obj, index):
        '''Initialiser for GapFree class'''

        super( BothRamp, self).__init__( exp_object, obj, index)
        self.resp_channel_1 = 'I-mon'
        self.resp_channel_2 = 'Adc-0'


    def plot_stimulus( self, ax):
        '''Plot stimulus'''
        return
        ax.plot( self.time, self.data[self.stim_channel], lw=2, color='black')


    def plot_response( self, ax):
        '''Plot response'''
        ax.plot( self.time, self.data[self.resp_channel_1], lw=2, color='dodgerblue')
        ax.plot( self.time, self.data[self.resp_channel_2], lw=2, color='orange')


