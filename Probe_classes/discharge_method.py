'''
    Enum for discharge method codes.
'''
from enum import Enum

class DischargeMethod(Enum):
    '''
        https://www.datadictionary.nhs.uk/data_elements/discharge_method_code__hospital_provider_spell_.html
    '''
    WITH_CONSENT        = 1
    BY_SELF_OR_RELATIVE = 2
    BY_ORDER            = 3
    PATIENT_DIED        = 4
    STILLBIRTH          = 5
    NOT_APPICABLE       = 8
    UNKNOWN             = 9

    @classmethod
    def column_name(cls) -> str:
        '''
        Returns the name of the column that contains the code.
        '''
        return "DISMETH"
