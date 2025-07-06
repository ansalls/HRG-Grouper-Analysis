'''
    This module is used to test the impact of secondary diagnoses on the HRG.
'''
from Probe_classes.code_drop import CodeDrop
from . import probe_base as pb


def probe_code_drop(no_cache: bool = False):
    '''
        For each row in the DataFrame, create additional rows with one fewer
        secondary codes, starting with the last secondary code.
        Updates the DIAG* columns and appends the class name and a diagnoses count
        to the spell ID field to ensure a unique identifier.

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
