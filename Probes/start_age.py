'''
# Hypothesis:
#  An HRG subchapter, and maybe an HRG chapter, may be DOB sensitive
#  and the sensitivity is based on age buckets, and those age buckets
#  will not be consistent but the total number of buckets is not large
#  - that is, under 18 vs over 18 are probably common, but exactly 21 or
#  - some other specific valuue are probably not common. Where there are
#  - ranges, those ranges probably appear elsewhere.

# This can't really be prodded too much without a dataset to work with,
# but the idea is to take a row from the output dataframe where we have
# a set of diagnoses and procedures, and an episode level HRG, and we
# loop through the possible ages and see if the HRG changes. If it does,
# we note the age range where it changes and the HRG, subchapter, and
# chapter, then we'll review the data to see if there is a pattern.

# Because age needs to be consistent between rows, we'll only take the
# first row of each spell and we'll append the age to the spell ID to make
# it unique.

# 1. load the data for a processed file into a dataframe
# 2. filter to the first row of each spell (EPIORDER == 1)
# 3. For each matching row, add the row to a new dataframe
# 4. Add rows like:
#       for age in range(0,100),
#       spell ID = f"{PROVSPNO}_{age}"
#       copy over the other elements, including the episode HRG
# 5. Save the new dataframe to a file
# 6. Run the grouper on the new file
# 7. Load the grouper output into a dataframe
# 8. Compare the episode HRG of the initial run, and if it differs...
#     - note the age range for which the new HRG appears,
#       the HRG chapter, the HRG subchapter, the grouping method (both before and after),
#       and the primary code associated with the grouping method (either the primary diagnosis
# or procedure)
'''

from Probe_classes.start_age import StartAge
from . import probe_base as pb


def probe_start_age(no_cache: bool = False):
    '''
    For each row in the DataFrame, create additional rows for each value
    of the StartAge class.
    Updates the 'start_age' column with the value and appends the
    class name and value to the 'PROVSPNO' field to ensure a unique identifier.

    Parameters:
    -----------
    df : pd.DataFrame
        The original DataFrame to which new rows will be appended.

    Returns:
    --------
    pd.DataFrame
        A new DataFrame containing both the original and the additional rows.
    '''
    pb.run_probe(StartAge, no_cache)
