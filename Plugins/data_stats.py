'''
    This module provides a data stats plugin that prints out statistics about the DataFrame.
'''
from typing import List
import pandas as pd
from Utils.constants import DIAGNOSIS_PREFIX, PROCEDURE_PREFIX
from Plugins.base_plugin import BasePlugin


class DataStatsPlugin(BasePlugin):
    '''
    A plugin that prints out statistics about the DataFrame.
    1. Range, mean, mode for each numeric column.
    2. Distinct count, top 5 for each non-numeric column.
    3. Lumped DIAG/OPER columns, counting total distinct codes + top 10.
    4. Spell-level stats:
        - # of spells (distinct PROVSPNO)
        - Avg episodes per spell
        - Count of spells that qualify for combination
          (i.e., > 1 row and consistent across key columns)
        - Count of single-episode spells
        - Count of inconsistent spells, plus how many had inconsistentcy on a given column.
    '''

    def __init__(self):
        '''
        Initialize the plugin with the prefixes for DIAG and OPER columns,
        '''
        self.diag_prefix = DIAGNOSIS_PREFIX
        self.oper_prefix = PROCEDURE_PREFIX

        # The columns that must match for a spell to be considered "consistent"
        self.check_columns = [
            'STARTAGE', 'SEX', 'CLASSPAT', 'ADMISORC', 'ADMIMETH',
            'MAINSPEF', 'TRETSPEF'
        ]

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        # We won't modify df at all—we'll just print stats and return the same DataFrame.
        print("\n===== Data Stats Plugin  =====")

        # 1. Per-column Stats
        self.print_column_stats(df)

        # 2. DIAG / OPER Groups
        self.print_diag_oper_stats(df)

        # 3. Spell Stats
        self.print_spell_stats(df)

        print("===== Done with Data Stats Plugin =====\n")

        return df

    # ----------------------------------------------------------------------
    # 1. Column-Level Stats
    # ----------------------------------------------------------------------
    def print_column_stats(self, df: pd.DataFrame):
        '''Print stats about each column in the DataFrame (except DIAG_*, OPER_*).'''
        diag_columns = [c for c in df.columns if c.startswith(self.diag_prefix)]
        oper_columns = [c for c in df.columns if c.startswith(self.oper_prefix)]
        skip = set(diag_columns + oper_columns)

        print("\n--- Per-Column Stats ---")
        for column in df.columns:
            if column in skip:
                continue

            # Attempt to treat column as numeric
            numeric_column = pd.to_numeric(df[column], downcast='integer', errors='coerce')
            non_null_count = numeric_column.notna().sum()
            # Threshold to decide if it's "really" numeric
            if non_null_count > 0.8 * len(numeric_column):
                column_min = numeric_column.min()
                column_max = numeric_column.max()
                column_mean = numeric_column.mean()
                # Nievely taking the first mode
                column_mode = numeric_column.mode(dropna=True)
                column_mode_str = column_mode.iloc[0] if not column_mode.empty else "No mode"

                print(f"\nColumn: {column}")
                print(f"  Range: {column_min} .. {column_max}")
                print(f"  Mean: {column_mean:.2f}")
                print(f"  Mode: {column_mode_str}")
                continue

            # Handle non-numeric columns
            distinct_count = df[column].nunique(dropna=True)
            top_5 = df[column].value_counts(dropna=True).head(5)

            print(f"\nColumn: {column}")
            print(f"  Distinct count: {distinct_count}")
            print("  Top 5 values:")
            for val, freq in top_5.items():
                print(f"    {val} => {freq}")

    # ----------------------------------------------------------------------
    # 2. DIAG / OPER Group Stats
    # ----------------------------------------------------------------------
    def print_diag_oper_stats(self, df: pd.DataFrame):
        '''Consider all DIAG columns as one group, and all OPER columns as one group.'''
        diag_columns = [column for column in df.columns if column.startswith(self.diag_prefix)]
        oper_columns = [column for column in df.columns if column.startswith(self.oper_prefix)]

        all_diag_vals = []
        for column in diag_columns:
            all_diag_vals.extend(df[column].dropna().tolist())

        diag_series = pd.Series(all_diag_vals, dtype=str)
        diag_distinct_count = diag_series.nunique()
        diag_top_10 = diag_series.value_counts().head(10)

        print("\n--- DIAG Group Stats ---")
        print(f"  Number of DIAG columns: {len(diag_columns)}")
        print(f"  Total codes: {len(all_diag_vals)}")
        print(f"  Distinct codes: {diag_distinct_count}")
        print("  Top 10 most common codes:")
        for val, freq in diag_top_10.items():
            print(f"    {val} => {freq}")

        all_oper_vals = []
        for column in oper_columns:
            all_oper_vals.extend(df[column].dropna().tolist())

        oper_series = pd.Series(all_oper_vals, dtype=str)
        oper_distinct_count = oper_series.nunique()
        oper_top_10 = oper_series.value_counts().head(10)

        print("\n--- OPER Group Stats ---")
        print(f"  Number of OPER columns: {len(oper_columns)}")
        print(f"  Total codes: {len(all_oper_vals)}")
        print(f"  Distinct codes: {oper_distinct_count}")
        print("  Top 10 most common codes:")
        for val, freq in oper_top_10.items():
            print(f"    {val} => {freq}")

    # ----------------------------------------------------------------------
    # 3. Spell-Level Stats
    # ----------------------------------------------------------------------
    def print_spell_stats(self, df: pd.DataFrame):
        '''
        - # of spells
        - Avg episodes per spell
        - Count of spells that qualify for combination
        - Count of single-episode spells
        - Count of inconsistent spells
        - Count of those inconsistencies by column
        '''

        print("\n--- Spell-Level Stats ---")
        if 'PROVSPNO' not in df.columns:
            print("  No 'PROVSPNO' column found. Can't compute spell-level stats.")
            return

        spells = df.groupby('PROVSPNO')
        spell_sizes = spells.size()  # number of rows per spell
        num_spells = len(spell_sizes)
        avg_episodes = spell_sizes.mean() if num_spells > 0 else 0

        qualifies_count = 0
        single_episode_count = 0
        inconsistent_count = 0

        # Track how many spells were inconsistent in each key column
        inconsistent_per_column = {column: 0 for column in self.check_columns}

        for _, spell_df in spells:
            size = len(spell_df)
            if size == 1:
                single_episode_count += 1
            else:
                # Check if consistent
                if self._all_values_identical(spell_df, self.check_columns):
                    qualifies_count += 1
                else:
                    # It's inconsistent
                    inconsistent_count += 1
                    # Figure out which columns are inconsistent
                    inc_columns = self._get_inconsistent_columns(spell_df, self.check_columns)
                    for column in inc_columns:
                        inconsistent_per_column[column] += 1

        print(f"  Total spells (distinct PROVSPNO): {num_spells}")
        print(f"  Average episodes per spell: {avg_episodes:.2f}")
        print(f"  Spells that qualify for combination: {qualifies_count}")
        print(f"  Single-episode spells (only 1 row): {single_episode_count}")
        print(f"  Inconsistent spells: {inconsistent_count}")
        print("\n  Inconsistency counts by column:")
        for column in self.check_columns:
            print(f"    {column} => {inconsistent_per_column[column]}")

    # ----------------------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------------------
    def _all_values_identical(self, df_subset: pd.DataFrame, columns: List[str]) -> bool:
        '''
        Returns True if for all columns in cols, the subset's rows
        have at most 1 distinct non-null value.
        '''
        for column in columns:
            if column not in df_subset.columns:
                # If the column doesn't exist, let's treat that as "identical" or skip
                continue
            unique_vals = df_subset[column].dropna().unique()
            if len(unique_vals) > 1:
                return False
        return True

    def _get_inconsistent_columns(self, df_subset: pd.DataFrame, columns: List[str]) -> List[str]:
        '''
        Return a list of columns that have more than 1 distinct non-null value.
        '''
        inconsistent_columns = []
        for column in columns:
            if column not in df_subset.columns:
                continue
            unique_vals = df_subset[column].dropna().unique()
            if len(unique_vals) > 1:
                inconsistent_columns.append(column)
        return inconsistent_columns
