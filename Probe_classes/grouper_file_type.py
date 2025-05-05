'''
    This module provides an enumeration of the values
    for treatment function codes.
'''
from enum import Enum

class GrouperFileType(Enum):
    '''
        The different types of files that are produced by the grouper
    '''
    INPUT = ''
    OUTPUT = '_output'
    FCE = '_FCE'
    FCE_REL = '_FCE_rel'
    FLAG = '_flag_rel'
    QUALITY = '_quality'
    QUALITY_REL = '_quality_rel'
    SORT = '_sort'
    SPELL = '_spell'
    SPELL_REL = '_spell_rel'
    SUMMARY = '_summary'
    UB = '_ub_rel'
