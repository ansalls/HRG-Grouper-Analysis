'''
This module contains utility functions for working with DataFrames housing
NHS Grouper data.
'''
import pandas as pd
from Plugins.column_extender import ColumnExtenderPlugin
from Utils.constants import (MAX_DIAG_COLS, MAX_OPER_COLS,
                             DIAGNOSIS_PREFIX, PROCEDURE_PREFIX)

def apply_plugins(df: pd.DataFrame, plugins: list):
    '''
    Applies each plugin in sequence to the DataFrame.
    '''
    for plugin in plugins:
        df = plugin.transform(df)
    return df

def write_output(df: pd.DataFrame, output_file_path: str, delimiter: str):
    '''
    Writes out the final DataFrame to a file
    '''
    # Output the CSV with header row, no index
    df.to_csv(output_file_path, sep=delimiter, index=False)

def expand_code_columns(df: pd.DataFrame):
    '''
    Expands the columns in the DataFrame based on the prefix and maximum number of columns.
    '''
    # Get the columns that start with the prefix
    plugins = [
        ColumnExtenderPlugin(prefix=DIAGNOSIS_PREFIX, maximum=MAX_DIAG_COLS),
        ColumnExtenderPlugin(prefix=PROCEDURE_PREFIX, maximum=MAX_OPER_COLS),
    ]

    apply_plugins(df, plugins)

    return df
