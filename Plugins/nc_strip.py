'''
This plugin is used to strip #NC (no code placeholder) from the diagnosis
codes in the grouper input data.
'''
import pandas as pd
from Utils.constants import DIAGNOSIS_PREFIX
from Plugins.base_plugin import BasePlugin

class NcStripPlugin(BasePlugin):
    '''
    Plugin that strips #NC placeholders from any columns whose names start with DIAG.
    '''

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        # Identify column names starting with 'DIAG' or 'OPER'
        columns_to_strip = []
        for column in df.columns:
            if column.startswith(DIAGNOSIS_PREFIX):
                columns_to_strip.append(column)

        for column in columns_to_strip:
            df[column] = df[column].str.replace('#NC', '')

        return df
