'''
This plugin expands the DIAG and OPER columns to the grouper maximum of 99 columns.
'''
import re
import pandas as pd
from Plugins.base_plugin import BasePlugin


class ColumnExtenderPlugin(BasePlugin):
    '''
    WARNING: This plugin modifies the structure of the dataframe!

    This plugin finds columns matching a given prefix + underscore + digits
    (e.g., DIAG_01, DIAG_02, etc.), determines the highest integer suffix,
    and inserts additional columns up to a specified max (e.g., DIAG_03, ... DIAG_99)
    immediately after the highest existing column.

    Example:
      - prefix = "DIAG", max = 99
      - If columns up to DIAG_16 exist, it inserts DIAG_17 ... DIAG_99
        right after DIAG_16.

    The purpose of this transformation is to enable consolidation of multi-episode
    spells into a single episode to simplify the data for the grouper. We'll need
    to append diagnoses and procedures to the end of the existing episode so we
    want to maximize the fields available to avoid dropping codes when the combined
    list might otherwise exceed the length of the original number of code fields.
    '''
    def __init__(self, prefix: str, maximum: int):
        '''
        :param prefix: The prefix, e.g. 'DIAG_' or 'OPER_'.
        :param max: The highest numeric suffix to append to.
        '''
        self.prefix = prefix
        self.maximum = maximum

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        # Regex to match prefix +  underscore + digits, e.g. DIAG_01, OPER_02, etc.
        pattern = r'^' + re.escape(self.prefix) + r'(\d+)$'
        regex = re.compile(pattern)

        # Track matching columns in a dict: column_name -> numeric_suffix
        matching_columns = {}
        for column in df.columns:
            match = regex.match(column)
            if match:
                # Grab the integer after the prefix
                numeric_suffix = int(match.group(1))
                matching_columns[column] = numeric_suffix

        # Figure out the largest suffix found, and the position of that column
        if not matching_columns:
            # No columns matching our prefix exist yet
            current_max = 0
            raise ValueError(f"No columns found matching prefix '{self.prefix}'")

        # Find the column with the highest numeric suffix
        last_column_name = max(matching_columns, key=lambda column: matching_columns[column])
        current_max = matching_columns[last_column_name]
        # Get that column's position
        last_column_position = df.columns.get_loc(last_column_name)

        # If we already meet or exceed desired_max, no new columns needed
        if current_max >= self.maximum:
            return df

        # Convert df.columns to a list so we can insert new column names
        column_list = list(df.columns)

        # Start adding new columns from current_max to max
        new_column_position = last_column_position
        for number in range(current_max + 1, self.maximum + 1):
            new_column_name = f"{self.prefix}{number:02d}"
            new_column_position += 1
            column_list.insert(new_column_position, new_column_name)

        # Reindex the DataFrame to include these new columns
        df = df.reindex(columns=column_list)

        return df
