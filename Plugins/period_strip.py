'''
This plugin is used to strip periods from the diagnosis and procedure
codes in the grouper input data.
'''
import pandas as pd
from Utils.constants import DIAGNOSIS_PREFIX, PROCEDURE_PREFIX
from Plugins.base_plugin import BasePlugin

class PeriodStripPlugin(BasePlugin):
    '''
    Plugin that strips periods from any columns whose names start with DIAG or OPER.
    The codesets use periods in the codes but the grouper requires they be removed.
    The number of procedure and diagnosis columns is configurable.
    '''

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        # Identify column names starting with 'DIAG' or 'OPER'
        columns_to_strip = []
        for column in df.columns:
            if column.startswith(DIAGNOSIS_PREFIX) or column.startswith(PROCEDURE_PREFIX):
                columns_to_strip.append(column)

        for column in columns_to_strip:
            df[column] = df[column].str.replace('.', '')

        return df
