'''
    This module provides an enumeration for the grouping method codes.
'''
from enum import StrEnum

class GroupingMethod(StrEnum):
    '''
        https://digital.nhs.uk/services/secondary-uses-service-sus/payment-by-results-guidance/sus-pbr-reference-manual/hrg-grouping
    '''

    BURN            = "B"
    DIAGNOSIS       = "D"
    GLOBAL          = "G"
    MULTIPLE_TRAUMA = "M"
    OUTPATIENT      = "O"
    PROCEDURE       = "P"
    ERROR           = "U"

    @classmethod
    def column_name(cls) -> str:
        '''
        Returns the name of the column that contains the code.
        '''
        return "GroupingMethodFlag"
