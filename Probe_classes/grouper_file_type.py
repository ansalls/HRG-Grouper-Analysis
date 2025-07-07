'''
    This module provides an enumeration of the various files created by the grouper.
'''
from enum import Enum
from Utils.constants import (
    FCE_HRG_FILE_SUFFIX,
    FCE_REL_HRG_FILE_SUFFIX,
    FLAG_HRG_FILE_SUFFIX,
    QUALITY_HRG_FILE_SUFFIX,
    QUALITY_REL_HRG_FILE_SUFFIX,
    SORT_HRG_FILE_SUFFIX,
    SPELL_HRG_FILE_SUFFIX,
    SPELL_REL_HRG_FILE_SUFFIX,
    SUMMARY_HRG_FILE_SUFFIX,
    UB_HRG_FILE_SUFFIX
)


class GrouperFileType(Enum):
    '''
        The different types of files that are produced by the grouper
    '''
    INPUT = ''
    OUTPUT = '_output'
    FCE = '_' + FCE_HRG_FILE_SUFFIX
    FCE_REL = '_' + FCE_REL_HRG_FILE_SUFFIX
    FLAG = '_' + FLAG_HRG_FILE_SUFFIX
    QUALITY = '_' + QUALITY_HRG_FILE_SUFFIX
    QUALITY_REL = '_' + QUALITY_REL_HRG_FILE_SUFFIX
    SORT = '_' + SORT_HRG_FILE_SUFFIX
    SPELL = '_' + SPELL_HRG_FILE_SUFFIX
    SPELL_REL = '_' + SPELL_REL_HRG_FILE_SUFFIX
    SUMMARY = '_' + SUMMARY_HRG_FILE_SUFFIX
    UB = '_' + UB_HRG_FILE_SUFFIX
