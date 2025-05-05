'''
    This module provides a plugin that finds sets of rows (grouped by PROVSPNO)
    where all rows share identical values for the columns:
    STARTAGE, SEX, CLASSPAT, ADMISORC, ADMIMETH, MAINSPEF, and TRETSPEF
'''
import pandas as pd
import numpy as np
from Utils.constants import DIAGNOSIS_PREFIX, PROCEDURE_PREFIX
from Plugins.base_plugin import BasePlugin


class CombinationRowPlugin(BasePlugin):
    '''
    This plugin finds sets of rows (grouped by PROVSPNO) where all rows share identical
    values for the columns:
      STARTAGE, SEX, CLASSPAT, ADMISORC, ADMIMETH, MAINSPEF, and TRETSPEF
    If all rows of that PROVSPNO share those values, we add a new 'combination' row.
    This new row is populated as follows:
      - PROVSPNO: original + "_C"
      - EPIORDER: 1
      - EPIDUR: sum of all EPIDUR values in the group
      - DIAG_01..DIAG_99: deduplicated set of codes from the group
      - OPER_01..OPER_99: deduplicated set of codes from the group
    Other columns are copied from the last row of the group.
    '''

    def __init__(self, replace_rows: bool = False):
        '''
        Constructor for the CombinationRowPlugin.
        :param replace_rows: If True, the original rows will be replaced with the combination row.
                            If False, the original rows will be kept.
        '''
        self.replace_rows = replace_rows


    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        # Define the columns that must match for all rows in a group
        check_columns = [
            'STARTAGE', 'SEX', 'CLASSPAT', 'ADMISORC', 'ADMIMETH',
            'MAINSPEF', 'TRETSPEF'
        ]

        # Columns to gather deduplicated values for
        # DIAG_01..DIAG_99 and OPER_01..OPER_99
        diag_columns = [column for column in df.columns if column.startswith(DIAGNOSIS_PREFIX)]
        oper_columns = [column for column in df.columns if column.startswith(PROCEDURE_PREFIX)]

        # We’ll build a list of new rows (in dict form) as we go
        processed_rows = []
        unique_spells = df['PROVSPNO'].unique()

        for spell in unique_spells:
            # Skip any spells that have already been combined.
            if isinstance(spell, str) and spell.endswith("_C"):
                # Append original rows unchanged
                for index in df[df['PROVSPNO'] == spell].index:
                    row_dict = df.loc[index].to_dict()
                    processed_rows.append(row_dict)
                continue

            # Subset of rows for this PROVSPNO
            spell_df = df[df['PROVSPNO'] == spell]

            # Check if all rows in spell_df share identical values for the columns in check_cols
            consistent = self._core_values_identical(spell_df, check_columns)

            # Add the original rows to new_rows in their current order
            # We'll do it one by one, so we know where the last row is
            if not self.replace_rows:
                for index in spell_df.index:
                    row_dict = df.loc[index].to_dict()
                    processed_rows.append(row_dict)

            # If consistent, we add a combination row right after the last row
            if consistent:
                # We'll base the new row mostly on the last row in this group
                last_idx = spell_df.index[-1]
                combo_row = df.loc[last_idx].to_dict()

                combo_row['PROVSPNO'] = str(combo_row['PROVSPNO']) + "_C"
                combo_row['EPIORDER'] = 1
                combo_row['EPIDUR'] = str(pd.to_numeric(spell_df['EPIDUR'], errors='coerce').sum())

                # For DIAG_* and OPER_* columns, gather distinct codes and place them in the new row
                combo_row = self._deduplicate_and_fill(spell_df, combo_row, diag_columns)
                combo_row = self._deduplicate_and_fill(spell_df, combo_row, oper_columns)

                # Insert the new row (dict) right after the last row
                processed_rows.append(combo_row)

        # Now convert new_rows back into a DataFrame
        result_df = pd.DataFrame(processed_rows, columns=df.columns)

        return result_df

    def _core_values_identical(self, spell_df: pd.DataFrame, columns: list) -> bool:
        '''
        Returns True if for all columns, the spell's rows have the same value.
        '''
        # If there's only one row, we can't combine it with anything
        if len(spell_df) == 1:
            return False

        for column in columns:
            unique_vals = spell_df[column].dropna().unique()
            if len(unique_vals) > 1:
                return False

        return True

    def _deduplicate_and_fill(self, spell_df: pd.DataFrame, combo_row: dict, columns: list) -> dict:
        '''
        Gathers distinct non-null values from all rows in "spell_df" for each column.
        Deduplicates them and add them to combo_row.
        Any leftover column positions get cleared.
        '''
        # Gather all distinct values from the group
        all_codes = set()
        for column in columns:
            if column in spell_df.columns:
                column_vals = spell_df[column].dropna().unique()
                if column_vals.size > 0:
                    all_codes.update(column_vals)

        # Deduplicate - could probably just use a set but that might scramble the order
        deduped_codes = list(all_codes)

        # Now place them into the new row
        for index, column in enumerate(columns):
            if index < len(deduped_codes):
                combo_row[column] = deduped_codes[index]
            else:
                # Clear out unused columns
                combo_row[column] = np.nan

        return combo_row
