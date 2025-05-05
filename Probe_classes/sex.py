'''
    This module provides an enumeration of sex codes.
'''
from enum import StrEnum

class Sex(StrEnum):
    '''
        An enumeration of the possible values for sex

        Source: https://www.datadictionary.nhs.uk/data_elements/person_phenotypic_sex.html
    '''
    NOT_KNOWN       = '0'   # Not in data dictionary but allowed in grouper
    MALE            = '1'
    FEMALE          = '2'
    INDETERMINATE   = '9'
    NOT_RECORDED    = 'X'

    @classmethod
    def column_name(cls) -> str:
        '''
        Returns the name of the column that contains the code.
        '''
        return "SEX"
