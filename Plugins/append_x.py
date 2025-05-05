'''
This plugin is used to append an X to short diagnosis codes
in the grouper input data.
'''
import pandas as pd
from Utils.constants import DIAGNOSIS_PREFIX
from Plugins.base_plugin import BasePlugin

class AppendXPlugin(BasePlugin):
    '''
    Plugin that appends an 'X' to any diagnosis codes that are 3 characters long.
    The grouper requires that short diagnosis codes be 4 characters long and
    X is the specified filler character.
    '''

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        # Identify column names starting with 'DIAG' or 'OPER'
        columns_to_update = []
        for column in df.columns:
            if column.startswith(DIAGNOSIS_PREFIX):
                columns_to_update.append(column)

        for column in columns_to_update:
            # Append 'X' to short diagnosis code (3 characters)
            df[column] = df[column].apply(
                lambda code: code + 'X' if isinstance(code,str) and len(code) == 3 else code
                )

        return df
