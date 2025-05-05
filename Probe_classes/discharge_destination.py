'''
    Enum for discharge destination codes.
'''
from enum import Enum

class DischargeDestination(Enum):
    '''
        https://www.datadictionary.nhs.uk/data_elements/destination_of_discharge__hospital_provider_spell_.html
    '''
    USUAL_PLACE_OF_RESIDENCE        = 19
    TEMPORARY_PLACE_OF_RESIDENCE    = 29
    REPATRIATION                    = 30
    COURT                           = 37
    PENAL_ESTABLISHMENT             = 40
    POLICE                          = 42
    HIGH_SEC_SCOTLAND               = 48
    NHS_OTHER_PROVIDER_HIGH_SEC     = 49
    NHS_OTHER_PROVIDER_MED_SEC      = 50
    NHS_OTHER_PROVIDER_GENERAL      = 51
    NHS_OTHER_PROVIDER_MATERNITY    = 52
    NHS_OTHER_PROVIDER_PSYCH        = 53
    CARE_HOME_NURSING               = 55
    CARE_HOME_NO_NURSING            = 56
    LOCAL_AUTHORITY                 = 65
    FOSTER_CARE                     = 66
    BORN_IN_OR_ON_WAY_TO_HOSPITAL   = 79
    PRIVATE_HOSPITAL_MED_SEC        = 84
    NON_NHS_CARE_HOME               = 85
    PRIVATE_HOSPITAL                = 87
    HOSPICE                         = 88
    REPATRIATION_ORG_RESPONSIBLE    = 89
    NOT_APPLICABLE                  = 98
    NOT_KNOWN                       = 99

    @classmethod
    def column_name(cls) -> str:
        '''
        Returns the name of the column that contains the code.
        '''
        return "DISDEST"
