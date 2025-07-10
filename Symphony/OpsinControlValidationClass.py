import numpy as np
from AbstractProtocolClass import AbstractProtocol
from matplotlib import pyplot as plt
from glob import glob

class OpsinControlValidation(AbstractProtocol):
    '''Class for OpsinControlValidation analysis'''

    def __init__(self, epoch_group_object, block_uuid, count):
        super(OpsinControlValidation, self).__init__(epoch_group_object, block_uuid, count)
        self.name = 'OpsinControlValidation'

        # Load properties into class object - NEED TO FIX THIS
        properties_group = self.group.get('properties')
        if properties_group:
            properties = properties_group.attrs

            for prop_pair in properties.items():
                setattr(self, prop_pair[0], prop_pair[1])
                self.pdf_vars.update({prop_pair[0]: prop_pair[1]})

        # Load parameters from file
        folder = '/Users/kylewedgwood/Dropbox/OpenEphys/+ac/+exeter/+wedgwoodlab/+protocols/HelperFunctions'
        #filepath = "%s/%s" % (folder, self['par_filename'].decode("utf-8"))

        # Find file using glob - NOT WORKING
        #filepath = glob('~/Dropbox/*/%s' % self['par_filename'].decode("utf-8"), recursive=True)
        #print(filepath)
        #data = np.genfromtxt(filepath, delimiter=',')
        #par_names = [ 'Gd1', 'Gd2', 'Gr', 'e12', 'e21', 'epsilon1', 'epsilon2', 'G', 'gamma', 'I_leak']
        #for (name, val) in zip(par_names, data[:,0]):
        #    self.pdf_vars.update({name: round(val,5)})


    def load_data(self):
        '''Loads data into array'''
        
        # Load stimulus from first epoch
        epoch = self.child_list[0]
        stimulus = epoch.fetch_light_stimulus('light340')
        self.noPts = len(stimulus)
        self.totalTime = self['noPts']/self['sampleRate']
        self.time = np.array( range( self['noPts']))/self['sampleRate']*1000.0 # time in ms
        response = np.zeros(shape=(self['noPts']))
        rep_count = 0

        for epoch in self.child_list:
            response += epoch.fetch_response()
            rep_count += 1


        response /= rep_count

        # Save back to class
        self.stimulus = stimulus
        self.response = response


    def fetch_total_time(self):
        '''Returns maximum time of protocol'''
        return 0


    def plot_stimulus(self, ax):
        '''Plots response based on stimulus pulses'''
        ax.plot(self.time, self.stimulus, lw=1.0, color='black')

        # Plot target current
        dt = 1.0/self['sampleRate']
        time, current = self.compute_target_current(dt, self['rise'], self['decay'], self['scale'])
        axR = ax.twinx()
        axR.plot(time, current, lw=1.0, color='red')


    def plot_response(self, ax):
        '''Plots response based on stimulus pulses'''
        ax.plot(self.time, self.response, lw=0.2, color='black')

        # Load model simulations - this is just an example for now
        folder = '/Users/kylewedgwood/Dropbox/OpenEphys/+ac/+exeter/+wedgwoodlab/+protocols/HelperFunctions'
        filepath = "%s/%s" % (folder, 'resampling_trajectories_2025-04-24_9_54')
        print(filepath)
        data = np.genfromtxt(filepath, delimiter=',')
        no_sample_pts = data.shape[1]
        time = 1000*np.linspace(0, self['totalTime'], no_sample_pts) # Time in ms

        for i in range(data.shape[0]):
            ax.plot(time, data[i,:])
        

    @staticmethod
    def compute_target_current(dt, rise, decay, scale):
        '''Calculates target currents'''
        # Rescale time to be in ms
        dt = dt*1000

        if (rise != decay):
            fun = lambda t: 1.0/(1.0/rise-1.0/decay)*(np.exp(-rise*t)-np.exp(-decay*t))
            tpeak = np.log(decay/rise)/(decay - rise)
            peak = -(decay*rise*(1.0/(decay/rise)**(decay/(decay-rise))-1.0/(decay/rise)**(rise/(decay-rise))))/(decay-rise)

        elif (rise == decay): # alpha synapse
            fun = lambda t: rise**2*t*np.exp(-rise*t)
            tpeak = 1.0/rise
            peak = rise*np.exp(-1)


        t0 = 0.0
        time = t0
        current = 0.0
        while (t0 < tpeak):
            t0 = t0+dt
            time = np.append(time, t0)
            current = np.append(current, fun(t0))

        i0 = tpeak
        while (i0 > 0.01*peak):
            t0 = t0+dt
            i0 = fun(t0)
            time = np.append(time, t0)
            current = np.append(current, i0)
        

        return time, scale*current