from BaseClass import Base
from PreparationClass import Preparation

class Subject( Base):
    '''Class to store subject data'''

    def __init__( self, exp_object, subject_uuid, count):
        '''Initialiser for Subject class'''

        self.group = exp_object.group.get( 'sources/' + subject_uuid)
        subject_pars = self.group.get( 'properties').attrs

        super( Subject, self).__init__( exp_object, subject_uuid, subject_pars, count)

        prep_list = self.group.get( 'sources/').keys()
        self.populate_list( prep_list, Preparation)


