
'''
This module is used to test the impact of Episode Duration on the HRG.
# Hypothesis:
#  The episode duration DOES impact the HRG.
#  Likely at subchapter level.
#  Probably not more than one cutoff point.
#  Probably not all that many and probably not consistent between instances
#  Perhaps a normal distribution
'''

from Probe_classes.episode_duration import EpisodeDuration
from . import probe_base as pb


def probe_episode_duration(no_cache: bool = False):
    '''
    For each row in the DataFrame, create additional rows for each value
    of the EpisodeDuration class.
    Updates the 'episode_duration' column with the value and appends the
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
    pb.run_probe(EpisodeDuration, no_cache)
