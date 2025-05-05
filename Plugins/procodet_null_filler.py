'''
Plugin that replaces any null values in the 'PROCODET' column with 'ZZZ'.
'''
import pandas as pd

from Plugins.base_plugin import BasePlugin

class ProcodetNullFillerPlugin(BasePlugin):
    '''
    Plugin that replaces any null values in the 'PROCODET' column with 'ZZZ'.
    This field is required by the grouper but the content of it doesn't matter.
    ZZZ is what's used in the example data.
    '''

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if 'PROCODET' in df.columns:
            df['PROCODET'] = df['PROCODET'].fillna("ZZZ")

        return df
