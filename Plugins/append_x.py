'''
    This plugin is used to append an PAD_CHARACTER to short diagnosis codes
    in the grouper input data. This is a requirement for the grouper
    to process short diagnosis codes correctly.
'''
import pandas as pd
from Utils.constants import DIAGNOSIS_PREFIX, SHORT_DIAG_LENGTH, PAD_CHARACTER
from Plugins.base_plugin import BasePlugin


class AppendXPlugin(BasePlugin):
    '''
        Plugin that appends an PAD_CHARACTER to any diagnosis codes that are short.
    '''

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        # Identify column names starting with the specified prefix
        columns_to_update = []
        for column in df.columns:
            if column.startswith(DIAGNOSIS_PREFIX):
                columns_to_update.append(column)

        for column in columns_to_update:
            # Appends PAD_CHARACTER to short diagnosis codes
            df[column] = df[column].apply(
                lambda code: code + PAD_CHARACTER if isinstance(code, str) and
                len(code) == SHORT_DIAG_LENGTH else code
            )
        return df
