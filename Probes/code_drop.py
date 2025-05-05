'''
This module is used to test the impact of secondary diagnoses and
procedure codes on the HRG.
'''
from Probe_classes.code_drop import CodeDrop
from . import probe_base as pb

def probe_code_drop(no_cache: bool = False):
    '''
    For each row in the DataFrame, create additional rows for with one less
    secondary code, starting with the last secondary procedure code.
    Updates the DIAG* aand OPER* columns and appends the
    class name and  a procedure and diagnoses count (D##P##) to the
    'PROVSPNO' field to ensure a unique identifier.

    Parameters:
    -----------
    df : pd.DataFrame
        The original DataFrame to which new rows will be appended.

    Returns:
    --------
    pd.DataFrame
        A new DataFrame containing both the original and the additional rows.
    '''
    pb.run_probe(CodeDrop, no_cache)
