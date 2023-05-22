from CellClass import Cell
from BaseClass import Base

class Preparation( Base):
    '''Class to store data for groups of cells'''

    def __init__( self, subject_object, prep_uuid, count):
        '''Initialiser for Preparation class'''

        self.group  = subject_object.group.get( 'sources/' + prep_uuid)
        prep_pars = self.group.get( 'properties').attrs

        super( Preparation, self).__init__( subject_object, prep_uuid, prep_pars, count)

        cell_list = self.group.get( 'sources/').keys()
        self.populate_list( cell_list, Cell)


    def check_tag( self, tag_name, val, exclude_list):
        '''Checks tag for generating include list'''
        tag_name = tag_name.upper()

        if tag_name == 'CATEGORY':
            self.check_tag_value( tag_name, val, exclude_list)

        else:
            super( Preparation, self).check_tag( tag_name, val, exclude_list)


        return exclude_list

