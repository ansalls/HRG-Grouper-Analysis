'''
    Enum for the AdmitSource codes.
'''
from enum import Enum

class AdmitSource(Enum):
    '''
        https://www.datadictionary.nhs.uk/data_elements/source_of_admission_code__hospital_provider_spell_.html
    '''

    USUAL_PLACE_OF_RESIDENCE        = 19
    TEMPORARY_PLACE_OF_RESIDENCE    = 29
    COURT                           = 39
    NHS_OTHER_PROVIDER_HIGH_SEC     = 49
    NHS_OTHER_PROVIDER_GENERAL      = 51
    NHS_OTHER_PROVIDER_MATERNITY    = 52
    NHS_OTHER_PROVIDER_PSYCH        = 53
    NHS_CARE_HOME                   = 54
    LOCAL_AUTHORITY                 = 65
    FOSTER_CARE                     = 66
    BORN_IN_OR_ON_WAY_TO_HOSPITAL   = 79
    NON_NHS_CARE_HOME               = 85
    PRIVATE_HOSPITAL                = 87
    NON_NHS_HOSPICE                 = 88
    NOT_APPLICABLE                  = 98
    NOT_KNOWN                       = 99

    @classmethod
    def column_name(cls) -> str:
        '''
        Returns the name of the column that contains the code.
        '''
        return "ADMISORC"
