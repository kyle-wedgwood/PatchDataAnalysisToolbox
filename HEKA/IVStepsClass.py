import matplotlib.pyplot as plt
from SeriesClass import Series

class IVSteps( Series):
    '''Class for GapFree analysis'''

    def __init__( self, exp_object, obj, index):
        '''Initialiser for VC-IC Class'''

        super( IVSteps, self).__init__( exp_object, obj, index)
        self.stim_channel = 'V-mon'
        self.resp_channel = 'I-mon'

        # Putting colormap options here
        self.cmap = self.create_color_map( 'Greys', len( self.child_list)+1)


    def plot_stimulus( self, ax):
        '''Plot stimulus'''
        for i in range( len( self.child_list)):
            ax.plot( self.time, self.data[self.stim_channel][:,i], lw=2, color=self.cmap[i])


    def plot_response( self, ax):
        '''Plot response'''
        for i in range( len( self.child_list)):
            ax.plot( self.time, self.data[self.resp_channel][:,i], lw=2, color=self.cmap[i])

