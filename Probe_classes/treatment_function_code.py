'''
    This module provides an enumeration of the values
    for treatment function codes.
'''
from enum import Enum

class TreatmentFunctionCode(Enum):
    '''
        https://www.datadictionary.nhs.uk/data_elements/activity_treatment_function_code.html
        Retired codes are not included
    '''
    # National Codes
    GENERAL_SURGERY                             = 100
    UROLOGY                                     = 101
    TRANSPLANT_SURGERY                          = 102
    BREAST_SURGERY                              = 103
    COLORECTAL_SURGERY                          = 104
    HEPATOBILIARY_AND_PANCREATIC_SURGERY        = 105
    UPPER_GASTROINTESTINAL_SURGERY              = 106
    VASCULAR_SURGERY                            = 107
    SPINAL_SURGERY                              = 108
    BARIATRIC_SURGERY                           = 109
    TRAUMA_AND_ORTHOPAEDIC                      = 110
    ORTHOPAEDIC                                 = 111
    ENDOCRINE_SURGERY                           = 113
    TRAUMA_SURGERY                              = 115
    EAR_NOSE_AND_THROAT                         = 120
    OPHTHALMOLOGY                               = 130
    ORAL_SURGERY                                = 140
    RESTORATIVE_DENTISTRY                       = 141
    ORTHODONTIC                                 = 143
    MAXILLOFACIAL_SURGERY                       = 144
    ORAL_AND_MAXILLOFACIAL_SURGERY              = 145
    NEUROSURGICAL                               = 150
    PLASTIC_SURGERY                             = 160
    BURNS_CARE                                  = 161
    CARDIOTHORACIC_SURGERY                      = 170
    CARDIAC_SURGERY                             = 172
    THORACIC_SURGERY                            = 173
    CARDIOTHORACIC_TRANSPLANTATION              = 174
    PAIN_MANAGEMENT                             = 191
    PAEDIATRIC_DENTISTRY                        = 142
    PAEDIATRIC_SURGERY                          = 171
    PAEDIATRIC_UROLOGY                          = 211
    PAEDIATRIC_TRANSPLANTATION_SURGERY          = 212
    PAEDIATRIC_GASTROINTESTINAL_SURGERY         = 213
    PAEDIATRIC_TRAUMA_AND_ORTHOPAEDIC           = 214
    PAEDIATRIC_EAR_NOSE_AND_THROAT              = 215
    PAEDIATRIC_OPHTHALMOLOGY                    = 216
    PAEDIATRIC_ORAL_AND_MAXILLOFACIAL_SURGERY   = 217
    PAEDIATRIC_NEUROSURGERY                     = 218
    PAEDIATRIC_PLASTIC_SURGERY                  = 219
    PAEDIATRIC_BURNS_CARE                       = 220
    PAEDIATRIC_CARDIAC_SURGERY                  = 221
    PAEDIATRIC_THORACIC_SURGERY                 = 222
    PAEDIATRIC_EPILEPSY                         = 223
    PAEDIATRIC_CLINICAL_PHARMACOLOGY            = 230
    PAEDIATRIC_PALLIATIVE_MEDICINE              = 240
    PAEDIATRIC_PAIN_MANAGEMENT                  = 241
    PAEDIATRIC_INTENSIVE_CARE                   = 242
    PAEDIATRIC_HEPATLOGY                        = 250
    PAEDIATRIC_GASTROENTEROLOGY                 = 251
    PAEDIATRIC_ENDOCRINOLOGY                    = 252
    PAEDIATRIC_CLINICAL_HAEMATOLOGY             = 253
    PAEDIATRIC_AUDIO_VESTIBULAR_MEDICINE        = 254
    PAEDIATRIC_CLINICAL_IMMUNOLOGY_AND_ALLERGY  = 255
    PAEDIATRIC_INFECTIOUS_DISEASES              = 256
    PAEDIATRIC_DERMATOLOGY                      = 257
    PAEDIATRIC_RESPIRATORY_MEDICINE             = 258
    PAEDIATRIC_NEPHROLOGY                       = 259
    PAEDIATRIC_MEDICAL_ONCOLOGY                 = 260
    PAEDIATRIC_INHERITED_METABOLIC_MEDICINE     = 261
    PAEDIATRIC_RHEUMATOLOGY                     = 262
    PAEDIATRIC_DIABETES                         = 263
    PAEDIATRIC_CYSTIC_FIBROSIS                  = 264
    PAEDIATRIC_EMERGENCY_MEDICINE               = 270
    PAEDIATRIC_INTERVENTIONAL_RADIOLOGY         = 280
    COMMUNITY_PAEDIATRIC                        = 290
    PAEDIATRIC_NEURODISABILITY                  = 291
    PAEDIATRIC_CARDIOLOGY                       = 321
    PAEDIATRIC_NEUROLOGY                        = 421
    EMERGENCY_MEDICINE                          = 180
    ANAESTHETIC                                 = 190
    INTENSIVE_CARE_MEDICINE                     = 192
    AVIATION_AND_SPACE_MEDICINE                 = 200
    GENERAL_INTERNAL_MEDICINE                   = 300
    GASTROENTEROLOGY                            = 301
    ENDOCRINOLOGY                               = 302
    CLINICAL_HAEMATOLOGY                        = 303
    CLINICAL_PHYSIOLOGY                         = 304
    CLINICAL_PHARMACOLOGY                       = 305
    HEPATOLOGY                                  = 306
    DIABETES                                    = 307
    BLOOD_AND_MARROW_TRANSPLANTATION            = 308
    HAEMOPHILIA                                 = 309
    AUDIO_VESTIBULAR_MEDICINE                   = 310
    CLINICAL_GENETICS                           = 311
    CLINICAL_IMMUNOLOGY_AND_ALLERGY             = 313
    REHABILITATION_MEDICINE                     = 314
    PALLIATIVE_MEDICINE                         = 315
    CLINICAL_IMMUNOLOGY                         = 316
    ALLERGY                                     = 317
    INTERMEDIATE_CARE                           = 318
    RESPITE_CARE                                = 319
    CARDIOLOGY                                  = 320
    CLINICAL_MICROBIOLOGY                       = 322
    SPINAL_INJURIES                             = 323
    ANTICOAGULANT                               = 324
    SPORT_AND_EXERCISE_MEDICINE                 = 325
    ACUTE_INTERNAL_MEDICINE                     = 326
    CARDIAC_REHABILITATION                      = 327
    STROKE_MEDICINE                             = 328
    TRANSIENT_ISCHAEMIC_ATTACK                  = 329
    DERMATOLOGY                                 = 330
    CONGENITAL_HEART_DISEASE                    = 331
    RARE_DISEASE                                = 333
    INHERITED_METABOLIC_MEDICINE                = 335
    RESPIRATORY_MEDICINE                        = 340
    RESPIRATORY_PHYSIOLOGY                      = 341
    PULMONARY_REHABILITATION                    = 342
    ADULT_CYSTIC_FIBROSIS                       = 343
    COMPLEX_SPECIALISED_REHABILITATION          = 344
    SPECIALIST_REHABILITATION                   = 345
    LOCAL_SPECIALIST_REHABILITATION             = 346
    SLEEP_MEDICINE                              = 347
    POST_COVID_19_SYNDROME                      = 348
    INFECTIOUS_DISEASES                         = 350
    TROPICAL_MEDICINE                           = 352
    GENITOURINARY_MEDICINE                      = 360
    RENAL_MEDICINE                              = 361
    MEDICAL_ONCOLOGY                            = 370
    NUCLEAR_MEDICINE                            = 371
    NEUROLOGY                                   = 400
    CLINICAL_NEUROPHYSIOLOGY                    = 401
    RHEUMATOLOGY                                = 410
    PAEDIATRIC                                  = 420
    NEONATAL_CRITICAL_CARE                      = 422
    WELL_BABY                                   = 424
    ELDERLY_MEDICINE                            = 430
    ORTHOGERIATRIC_MEDICINE                     = 431
    DENTAL_MEDICINE                             = 450
    SPECIAL_CARE_DENTISTRY                      = 451
    MEDICAL_OPHTHALMOLOGY                       = 460
    OPHTHALMIC_AND_VISION_SCIENCE               = 461
    OBSTETRICS                                  = 501
    GYNAECOLOGY                                 = 502
    GYNAECOLOGICAL_ONCOLOGY                     = 503
    COMMUNITY_SEXUAL_AND_REPRODUCTIVE_HEALTH    = 504
    FETAL_MEDICINE                              = 505
    MIDWIFERY                                   = 560
    CLINICAL_PSYCHOLOGY                         = 656
    LEARNING_DISABILITY                         = 700
    ADULT_MENTAL_HEALTH                         = 710
    CHILD_AND_ADOLESCENT_PSYCHIATRY             = 711
    FORENSIC_PSYCHIATRY                         = 712
    MEDICAL_PSYCHOTHERAPY                       = 713
    OLD_AGE_PSYCHIATRY                          = 715
    EATING_DISORDERS                            = 720
    ADDICTION                                   = 721
    LIAISON_PSYCHIATRY                          = 722
    PSYCHIATRIC_INTENSIVE_CARE                  = 723
    PERINATAL_MENTAL_HEALTH                     = 724
    MENTAL_HEALTH_RECOVERY_AND_REHABILITATION   = 725
    MENTAL_HEALTH_DUAL_DIAGNOSIS                = 726
    DEMENTIA_ASSESSMENT                         = 727
    NEUROPSYCHIATRY                             = 730
    CLINICAL_ONCOLOGY                           = 800
    INTERVENTIONAL_RADIOLOGY                    = 811
    DIAGNOSTIC_IMAGING                          = 812
    CHEMICAL_PATHOLOGY                          = 822
    MEDICAL_VIROLOGY                            = 834
    PHYSIOTHERAPY                               = 650
    OCCUPATIONAL_THERAPY                        = 651
    SPEECH_AND_LANGUAGE_THERAPY                 = 652
    PODIATRY                                    = 653
    DIETETICS                                   = 654
    ORTHOPTICS                                  = 655
    PROSTHETICS                                 = 657
    ORTHOTICS                                   = 658
    DRAMATHERAPY                                = 659
    ART_THERAPY                                 = 660
    MUSIC_THERAPY                               = 661
    OPTOMETRY                                   = 662
    PODIATRIC_SURGERY                           = 663
    UROLOGICAL_PHYSIOLOGY                       = 670
    VASCULAR_PHYSIOLOGY                         = 673
    CARDIAC_PHYSIOLOGY                          = 675
    GASTROINTESTINAL_PHYSIOLOGY                 = 677
    AUDIOLOGY                                   = 840
    DIABETIC_EDUCATION                          = 920

    # Default Codes
    # Non-UK provider; TREATMENT FUNCTION not known, treatment mainly surgical
    NON_UK_PROVIDER_SURGICAL                    = 199
    # Non-UK provider; TREATMENT FUNCTION not known, treatment mainly medical
    NON_UK_PROVIDER_MEDICAL                     = 499

    @classmethod
    def column_name(cls) -> str:
        '''
        Returns the name of the column that contains the code.
        '''
        return "TRETSPEF"
