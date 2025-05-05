'''
This module is used to test the impact of admit source on the HRG.
'''
from Probe_classes.sex import Sex
from . import probe_base as pb
# Hypothesis:
#  HRGs are not sensitive to sex

# Hypothesis:
#  The grouper is sensitive to sex and will error when there's a conflict
#  between the sex of the patient and that allowed for specific procedures
#  or diagnoses. (e.g. male with pregnancy related diagnosis)
# FALSE! O001, N809, E282, and C539 were all considered valid for a male patient

def probe_sex(no_cache: bool = False):
    '''
    For each row in the DataFrame, create additional rows for each member
    of the Sex enum.
    Updates the 'sex' column with the enum member's value and appends the
    enum class name and the enum member's name to the 'PROVSPNO' field
    to ensure a unique identifier.

    Parameters:
    -----------
    df : pd.DataFrame
        The original DataFrame to which new rows will be appended.

    Returns:
    --------
    pd.DataFrame
        A new DataFrame containing both the original and the additional rows.
    '''
    pb.run_probe(Sex, no_cache)