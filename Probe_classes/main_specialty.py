'''
    Enum for Main Specialty codes.
'''
from enum import Enum

class MainSpecialty(Enum):
    '''
        datadictionary.nhs.uk/data_elements/care_professional_main_specialty_code.html
        Retired codes are not included
        500 also not included after verifying that the grouper wont accept it.
    '''
    GENERAL_SURGERY                             = 100
    UROLOGY                                     = 101
    VASCULAR_SURGERY                            = 107
    TRAUMA_AND_ORTHOPAEDICS                     = 110
    EAR_NOSE_AND_THROAT                         = 120
    OPHTHALMOLOGY                               = 130
    ORAL_SURGERY                                = 140
    RESTORATIVE_DENTISTRY                       = 141
    PAEDIATRIC_DENTISTRY                        = 142
    ORTHODONTICS                                = 143
    ORAL_AND_MAXILLOFACIAL_SURGERY              = 145
    ENDODONTICS                                 = 146
    PERIODONTICS                                = 147
    PROSTHODONTICS                              = 148
    SURGICAL_DENTISTRY                          = 149
    NEUROSURGERY                                = 150
    PLASTIC_SURGERY                             = 160
    CARDIOTHORACIC_SURGERY                      = 170
    PAEDIATRIC_SURGERY                          = 171
    EMERGENCY_MEDICINE                          = 180
    ANAESTHETICS                                = 190
    INTENSIVE_CARE_MEDICINE                     = 192
    AVIATION_AND_SPACE_MEDICINE                 = 200
    GENERAL_INTERNAL_MEDICINE                   = 300
    GASTROENTEROLOGY                            = 301
    ENDOCRINOLOGY_AND_DIABETES                  = 302
    CLINICAL_HAEMATOLOGY                        = 303
    CLINICAL_PHYSIOLOGY                         = 304
    CLINICAL_PHARMACOLOGY                       = 305
    AUDIO_VESTIBULAR_MEDICINE                   = 310
    CLINICAL_GENETICS                           = 311
    CLINICAL_IMMUNOLOGY                         = 313
    REHABILITATION_MEDICINE                     = 314
    PALLIATIVE_MEDICINE                         = 315
    ALLERGY                                     = 317
    CARDIOLOGY                                  = 320
    PAEDIATRIC_CARDIOLOGY                       = 321
    SPORT_AND_EXERCISE_MEDICINE                 = 325
    ACUTE_INTERNAL_MEDICINE                     = 326
    DERMATOLOGY                                 = 330
    RESPIRATORY_MEDICINE                        = 340
    INFECTIOUS_DISEASES                         = 350
    TROPICAL_MEDICINE                           = 352
    GENITOURINARY_MEDICINE                      = 360
    RENAL_MEDICINE                              = 361
    MEDICAL_ONCOLOGY                            = 370
    NUCLEAR_MEDICINE                            = 371
    NEUROLOGY                                   = 400
    CLINICAL_NEUROPHYSIOLOGY                    = 401
    RHEUMATOLOGY                                = 410
    PAEDIATRICS                                 = 420
    PAEDIATRIC_NEUROLOGY                        = 421
    GERIATRIC_MEDICINE                          = 430
    DENTAL_MEDICINE                             = 450
    SPECIAL_CARE_DENTISTRY                      = 451
    MEDICAL_OPHTHALMOLOGY                       = 460
    OBSTETRICS                                  = 501
    GYNAECOLOGY                                 = 502
    COMMUNITY_SEXUAL_AND_REPRODUCTIVE_HEALTH    = 504
    MIDWIFERY                                   = 560
    GENERAL_MEDICAL_PRACTICE                    = 600
    GENERAL_DENTAL_PRACTICE                     = 601
    LEARNING_DISABILITY                         = 700
    ADULT_MENTAL_ILLNESS                        = 710
    CHILD_AND_A_DOLESCENT_PSYCHIATRY            = 711
    FORENSIC_PSYCHIATRY                         = 712
    MEDICAL_PSYCHOTHERAPY                       = 713
    OLD_AGE_PSYCHIATRY                          = 715
    CLINICAL_ONCOLOGY                           = 800
    RADIOLOGY                                   = 810
    GENERAL_PATHOLOGY                           = 820
    BLOOD_TRANSFUSION                           = 821
    CHEMICAL_PATHOLOGY                          = 822
    HAEMATOLOGY                                 = 823
    HISTOPATHOLOGY                              = 824
    IMMUNOPATHOLOGY                             = 830
    MEDICAL_MICROBIOLOGY_AND_VIROLOGY           = 831
    MEDICAL_MICROBIOLOGY                        = 833
    MEDICAL_VIROLOGY                            = 834
    COMMUNITY_MEDICINE                          = 900
    OCCUPATIONAL_MEDICINE                       = 901
    COMMUNITY_HEALTH_SERVICES_DENTAL            = 902
    PUBLIC_HEALTH_MEDICINE                      = 903
    PUBLIC_HEALTH_DENTAL                        = 904
    NURSING                                     = 950
    ALLIED_HEALTH_PROFESSIONAL                  = 960

    # Default Codes
    # Non-UK provider; specialty function not known, treatment mainly surgical
    NON_UK_SPECIALTY_SURGICAL                   = 199
    # Non-UK provider; specialty function not known, treatment mainly medical
    NON_UK_SPECIALTY_MEDICAL                    = 499

    @classmethod
    def column_name(cls) -> str:
        '''
        Returns the name of the column that contains the code.
        '''
        return "MAINSPEF"
