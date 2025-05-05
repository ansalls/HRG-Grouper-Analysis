'''
    This module provides a plugin that finds sets of rows (grouped by PROVSPNO)
    where all rows share identical values for the columns:
    STARTAGE, SEX, CLASSPAT, ADMISORC, ADMIMETH, MAINSPEF, and TRETSPEF
'''
import pandas as pd
from Plugins.base_plugin import BasePlugin


class OnlySingleEpisodeSpellsPlugin(BasePlugin):
    '''
        This plugin removes rows where EPIORDER is greater than 1
        so that we don't have to account for cross-episode interaction
        within the grouper (which is known to occur)
    '''
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        '''
        Filters the input DataFrame to remove any rows where EPIORDER is greater than 1.

        Parameters:
        -----------
        df : pd.DataFrame
            The input DataFrame, expected to include an 'EPIORDER' column.

        Returns:
        --------
        pd.DataFrame
            A new DataFrame containing only the rows where EPIORDER is 1 or less.
        '''
        if 'EPIORDER' not in df.columns:
            raise ValueError("The input DataFrame must contain an 'EPIORDER' column.")

        # Identify the indices of rows where EPIORDER is greater than 1
        rows_to_drop = df.index[df['EPIORDER'] > 1]

        df.drop(index=rows_to_drop, inplace=True)

        return df
