'''
    This module provides a plugin that randomizes the 'STARTAGE' column.
'''
import random
import pandas as pd
from Plugins.base_plugin import BasePlugin


class AgeAnonymizerPlugin(BasePlugin):
    '''
    If the 'STARTAGE' is between 25 and 40, replace it with a new value
    in the same range.
    TODO: As buckets are identified, add them here and add this to the
    plugin list.
    '''
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if 'STARTAGE' in df.columns:
            mask = (df['STARTAGE'] > 25) & (df['STARTAGE'] < 40)

            df.loc[mask, 'STARTAGE'] = [
                random.randint(25, 40) for _ in range(mask.sum())
            ]
        return df
