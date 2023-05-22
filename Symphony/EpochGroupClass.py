from BaseClass import Base
from Protocols import protocols, excluded_protocols

class EpochGroup( Base):
    '''Class to store data for epoch groups'''

    def __init__( self, cell_object, epoch_group_uuid, count):
        '''Initialiser for EpochGroup class'''

        self.group = cell_object.group.get( 'epochGroups/' + epoch_group_uuid)
        epoch_group_pars = { 'label': self.group.attrs['label']}

        super( EpochGroup, self).__init__( cell_object, epoch_group_uuid, \
                epoch_group_pars, count)
        self.populate_epoch_block_list()


    def populate_epoch_block_list( self):
        '''Add epoch blocks uuids to class object'''
        blocks_list = self.group.get( 'epochBlocks').keys()
        for block_counter, block_uuid in enumerate( blocks_list):
            name = block_uuid.split( '.')[-1]
            name = name.split( '-')[0]

            if name in excluded_protocols:
                continue

            self.add_child( protocols[name], block_uuid, block_counter)

        # Now reorder according to the time created
        start_times = []
        for child in self.child_list:
            start_times.append( child.start_time)


        # Renumber according to ordered list
        self.child_list = [ child for _, child in sorted( zip( start_times, self.child_list))]
        for no, child in enumerate( self.child_list):
            child.no = no

