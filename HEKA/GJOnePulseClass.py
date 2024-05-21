import matplotlib.pyplot as plt
from SeriesClass import Series

class GJOnePulse( Series):
    '''Class for one gap junction pulse analysis'''

    def __init__( self, exp_object, obj, index):
        '''Initialiser for one gap junction pulse class'''

        super( GJOnePulse, self).__init__( exp_object, obj, index)
        self.resp_channel_1 = 'I-mon'
        self.resp_channel_2 = 'Adc-0'

        # Putting colormap options here
        self.cmap_1 = self.create_color_map( 'Blues', len( self.child_list)+1)
        self.cmap_2 = self.create_color_map( 'Oranges', len( self.child_list)+1)


    def plot_stimulus( self, ax):
        '''Plot stimulus'''
        return
        ax.plot( self.time, self.data[self.stim_channel], lw=2, color='black')


    def plot_response( self, ax):
        '''Plot response'''
        for i in range( len( self.child_list)):
            ax.plot( self.time, self.data[self.resp_channel_1][:,i], lw=2, color=self.cmap_1[i])
            ax.plot( self.time, self.data[self.resp_channel_2][:,i], lw=2, color=self.cmap_2[i])


