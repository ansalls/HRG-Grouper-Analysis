'''
This module is used to test the impact of admit source on the HRG.
'''
from Probe_classes.treatment_function_code import TreatmentFunctionCode
from . import probe_base as pb
# Hypothesis:
#  The TFC does not impact the HRG.

def probe_treatment_function_code(no_cache: bool = False):
    '''
    For each row in the DataFrame, create additional rows for each member
    of the TreatmentFunctionCode enum.
    Updates the 'treatment_function_code' column with the enum member's value and appends the
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
    pb.run_probe(TreatmentFunctionCode, no_cache)
