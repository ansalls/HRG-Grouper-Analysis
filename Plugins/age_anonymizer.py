'''
    This module provides a plugin that randomizes the START_AGE column.
'''
import random
import pandas as pd
from Plugins.base_plugin import BasePlugin
from Utils.constants import START_AGE


class AgeAnonymizerPlugin(BasePlugin):
    '''
        If the START_AGE is between 25 and 40, replace it with a new value
        in the same range.
        TODO: As buckets are identified, add them here and add this to the
        plugin list.
    '''

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if START_AGE in df.columns:
            mask = (df[START_AGE] > 25) & (df[START_AGE] < 40)

            df.loc[mask, START_AGE] = [
                random.randint(25, 40) for _ in range(mask.sum())
            ]
        return df
