'''
    Enum for Admit Method codes.
'''
from enum import StrEnum

class AdmitMethod(StrEnum):
    '''
        https://www.datadictionary.nhs.uk/data_elements/admission_method_code__hospital_provider_spell_.html
    '''

    # Elective Admission
    ELECTIVE_WAITING_LIST   = "11"  # Elective Admission: Waiting list
    ELECTIVE_BOOKED         = "12"  # Elective Admission: Booked
    ELECTIVE_PLANNED        = "13"  # Elective Admission: Planned

    # Emergency Admission
    EMERGENCY_ED            = "21"  # Emergency Admission: Emergency Care Department
                                    # or dental casualty department
    EMERGENCY_GP            = "22"  # Emergency Admission: GENERAL PRACTITIONER direct admission
    EMERGENCY_BED_BUREAU    = "23"  # Emergency Admission: Bed bureau
    EMERGENCY_CONSULTANT    = "24"  # Emergency Admission: Consultant Clinic
    EMERGENCY_MH_CRT        = "25"  # Emergency Admission: Admission via Mental Health Crisis Team
    EMERGENCY_ED_OTHER      = "2A"  # Emergency Admission: Emergency Care Department of
                                    # another provider where the patient hadn't been admitted
    EMERGENCY_TRANSFER      = "2B"  # Emergency Admission: Transfer of an admitted patient from
                                    # another Hospital Provider in an emergency
    EMERGENCY_BABY_HOME     = "2C"  # Emergency Admission: Baby born at home as intended
    EMERGENCY_OTHER         = "2D"  # Emergency Admission: Other emergency admission
    EMERGENCY_OTHER_MEANS   = "28"  # Emergency Admission: Other means (not sure how this is
                                    # different from above options...)

    # Maternity Admission
    MATERNITY_ANTE_PARTUM   = "31"  # Maternity Admission: Admitted ante partum
    MATERNITY_POST_PARTUM   = "32"  # Maternity Admission: Admitted post partum

    # Other Admission
    OTHER_BIRTH_IN_HCP      = "82"  # Other Admission: The birth of a baby in this
                                    #Health Care Provider
    OTHER_BABY_OUTSIDE      = "83"  # Other Admission: Baby born outside the Health Care
                                    # Provider except when born at home as intended
    OTHER_TRANSFER          = "81"  # Other Admission: Transfer of any admitted patient from
                                    # other Hospital Provider other than in an emergency

    # Default Codes
    NOT_APPLICABLE          = "98"  # Not applicable
    UNKNOWN                 = "99"  # Unknown

    @classmethod
    def column_name(cls) -> str:
        '''
        Returns the name of the column that contains the admit method code.
        '''
        return "ADMIMETH"

    @classmethod
    def admit_type(cls, method: "AdmitMethod") -> str:
        '''
        Returns "ELE" if the admission source is elective (codes 11, 12, 13),
        otherwise returns "NON" for non-elective.
        '''
        if method in (cls.ELECTIVE_WAITING_LIST,
                      cls.ELECTIVE_BOOKED,
                      cls.ELECTIVE_PLANNED):
            return "ELE"

        return "NON"
