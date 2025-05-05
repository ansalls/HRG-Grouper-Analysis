'''
    Enum for Patient Classification codes.
'''
from enum import Enum

class PatientClassification(Enum):
    '''
        https://www.datadictionary.nhs.uk/data_elements/patient_classification_code.html
    '''
    ORDINARY        = 1
    DAY_CASE        = 2
    REGULAR_DAY     = 3
    REGULAR_NIGHT   = 4
    DELIVERY        = 5
    NOT_APPLICABLE  = 8

    @classmethod
    def column_name(cls) -> str:
        '''
        Returns the name of the column that contains the code.
        '''
        return "CLASSPAT"

    @classmethod
    def spell_type(cls, classification: 'PatientClassification') -> str:
        '''
        Returns "DAY" if the patient classification is day case (2),
        returns "ORD" if the patient classification is ordinary, regular day,
        or regular night (1, 3, 4). This is a key component in the tariff kv
        store that originates from the spell type in the tariff data file.
        '''
        if classification == cls.DAY_CASE:
            return "DAY"
        if classification in (cls.ORDINARY, cls.REGULAR_DAY, cls.REGULAR_NIGHT):
            return "ORD"
        return "UNK"
        #raise ValueError(f"Unexpected patient classification: {classification}")
