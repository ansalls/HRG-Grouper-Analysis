'''
    Plugin that replaces any null values in the ORGANIZATION_ID column with 'ZZZ'.
'''
import pandas as pd
from Plugins.base_plugin import BasePlugin
from Utils.constants import ORGANIZATION_ID


class ProcodetNullFillerPlugin(BasePlugin):
    '''
        Plugin that replaces any null values in the ORGANIZATION_ID column with 'ZZZ'.
        This field is required by the grouper but the content of it doesn't matter.
        ZZZ is what's used in the example data.
    '''

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if ORGANIZATION_ID in df.columns:
            df[ORGANIZATION_ID] = df[ORGANIZATION_ID].fillna("ZZZ")

        return df
