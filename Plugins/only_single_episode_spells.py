'''
    This module provides a plugin that drops all rows where the EPISODE_SEQUENCE_NUMBER
    is greater than 1. This is useful for ensuring that we only work with single-episode spells,
    avoiding complications from cross-episode interactions.
'''
import pandas as pd
from Plugins.base_plugin import BasePlugin
from Utils.constants import EPISODE_SEQUENCE_NUMBER


class OnlySingleEpisodeSpellsPlugin(BasePlugin):
    '''
        This plugin removes rows where EPISODE_SEQUENCE_NUMBER is greater than 1
        so that we don't have to account for cross-episode interaction
        within the grouper (which is known to occur)
    '''

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        '''
            Filters the input DataFrame to remove any rows where EPISODE_SEQUENCE_NUMBER > 1.

            Parameters:
            -----------
            df : pd.DataFrame
                The input DataFrame, expected to include an EPISODE_SEQUENCE_NUMBER column.

            Returns:
            --------
            pd.DataFrame
                A new DataFrame containing only the rows where EPISODE_SEQUENCE_NUMBER is 1 or less.
        '''
        if EPISODE_SEQUENCE_NUMBER not in df.columns:
            raise ValueError(
                f"The input DataFrame must contain an {EPISODE_SEQUENCE_NUMBER} column.")

        # Identify the indices of rows where EPISODE_SEQUENCE_NUMBER is greater than 1
        rows_to_drop = df.index[df[EPISODE_SEQUENCE_NUMBER] > 1]

        df.drop(index=rows_to_drop, inplace=True)

        return df
