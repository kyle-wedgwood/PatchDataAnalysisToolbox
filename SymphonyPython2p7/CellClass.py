from BaseClass import Base
from EpochGroupClass import EpochGroup

class Cell( Base):
    '''Class to store parameters for individual cell'''

    def __init__( self, prep_object, cell_uuid, count):
        '''Initialiser for Cell object'''

        self.group = prep_object.group.get( 'sources/' + cell_uuid)
        cell_pars = self.group.get( 'properties').attrs

        super( Cell, self).__init__( prep_object, cell_uuid, cell_pars, count)

        epoch_group_list = self.group.get( 'epochGroups').keys()
        self.populate_list( epoch_group_list, EpochGroup)


    def check_tag( self, tag_name, val, exclude_list):
        '''Checks tag for generating include list'''
        tag_name = tag_name.upper()

        if tag_name == 'GFP':
            exclude_list = self.check_tag_value( tag_name, val, exclude_list)


        return exclude_list


    def fetch_protocol_uuids( self, protocol_uuids, exclude_repeats=False, exclude_list=[]):
        '''Overloading to only allow one of each type of protocol per cell'''
        if exclude_repeats:

            protocol_names = []
            cell_protocol_uuids = []
            super( Cell, self).fetch_protocol_uuids( cell_protocol_uuids)

            # Need to fix to replace any protocols excluded by user
            for uuid in cell_protocol_uuids:
                name = uuid.split( '-')[0]
                if (name not in protocol_names) & (uuid not in exclude_list):
                    protocol_uuids.append( uuid)
                    protocol_names.append( name)

        else:
            super( Cell, self).fetch_protocol_uuids( protocol_uuids)


