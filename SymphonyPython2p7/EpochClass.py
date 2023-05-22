from BaseClass import Base

class Epoch( Base):
    '''Class to hold epochs, for consistency with other classes'''

    def __init__( self, protocol_object, epoch_uuid, count):
        '''Initialiser for Epoch class'''

        self.group = protocol_object.group.get( 'epochs/' + epoch_uuid)

        super( Epoch, self).__init__( protocol_object, epoch_uuid, {}, count)


    def fetch_response( self, amp='Amp'):
        '''Gets response data from epoch'''
        response_group = self.group.get( 'responses')
        for response_uuid in response_group.keys():
            if amp in response_uuid:
                break

        response_data = response_group.get( response_uuid + '/data')
        return response_data['quantity']


    def fetch_dynamic_clamp_input( self, amp):
        '''Fetches dynamic clamp response associated with specified amplifier'''
        response_group = self.group.get( 'responses')
        if amp == 'Amp1':
            response_name = 'DC1input'
        elif amp == 'Amp2':
            response_name = 'DC2input'

        for response_uuid in response_group.keys():
            if response_name in response_uuid:
                break

        response_data = response_group.get( response_uuid + '/data')
        return 400*response_data['quantity']


    def fetch_stimulus_pars( self):
        '''Gets stimulus parameters for this epoch'''
        stim_pars = {}
        stimulus_group = self.group.get( 'stimuli')
        uuid = stimulus_group.visit( lambda name: self.find_string( name, 'Amp'))
        protocol_pars = stimulus_group.get( uuid + '/parameters').attrs
        for key, val in protocol_pars.items():
            stim_pars[key] = val

        # Now fetch any specific parameters
        if 'protocolParameters' in self.group.keys():
            protocol_pars = self.group.get ( 'protocolParameters').attrs
            for key, val in protocol_pars.items():
                stim_pars[key] = val


        return stim_pars


    def fetch_stimulus_properties( self):
        '''Gets stimulus properties for this epoch'''
        if 'properties' in self.group.keys():
            return self.group.get( 'properties').attrs
        else:
            return {}


    def fetch_stimulus( self, amp='Amp'):
        '''Fetch stimulus if it exists'''
        stim_group = self.group.get( 'stimuli')
        for stim_uuid in stim_group.keys():
            if amp in stim_uuid:
                break

        if 'data' in stim_group.get( stim_uuid).keys():
            stim_data = stim_group.get( stim_uuid + '/data')
            return stim_data['quantity']

        else:
            print( 'No data found')
            return


    @staticmethod
    def find_string( name, string):
        '''Return name if it contains string'''
        if string in name:
            return name

