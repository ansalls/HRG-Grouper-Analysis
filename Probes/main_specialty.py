'''
This module is used to test the impact of main specialty on the HRG.
'''
from Probe_classes.main_specialty import MainSpecialty
from . import probe_base as pb
# Hypothesis:
#  The main specialty doesn't impact the HRG.

def probe_main_specialty(no_cache: bool = False):
    '''
    For each row in the DataFrame, create additional rows for each member
    of the MainSpecialty enum.
    Updates the 'main_specialty' column with the enum member's value and appends the
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
    pb.run_probe(MainSpecialty, no_cache)
