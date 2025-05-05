'''
This module is used to test the impact of admit source on the HRG.
'''
from Probe_classes.patient_classification import PatientClassification
from . import probe_base as pb
# Hypothesis:
#  Patient classification doesn't not impact HRG grouping
#  But it DOES impact Reimbursement (obvious from tariff file)

def probe_patient_classification(no_cache: bool = False):
    '''
    For each row in the DataFrame, create additional rows for each member
    of the PatientClassification enum.
    Updates the 'patient_classification' column with the enum member's value and appends the
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
    pb.run_probe(PatientClassification, no_cache)
