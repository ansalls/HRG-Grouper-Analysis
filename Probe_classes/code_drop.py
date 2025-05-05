'''
    Class for Code Drop(ping).
'''
import itertools
import pandas as pd
from tqdm import tqdm  # Add this import

from Utils.constants import (DEFAULT_DELIMITER,
                             DIAGNOSIS_PREFIX) #,PROCEDURE_PREFIX)

class CodeDrop:
    '''
    Class for incrementally dropping diagnoses codes.
    '''
    @staticmethod
    def generate_new_rows(row: pd.Series) -> list[pd.Series]:
        """
        Legacy row-by-row implementation (slow for large data).
        """
        new_rows = []

        # Identify DIAG and OPER columns
        diag_cols = [col for col in row.index if col.startswith(DIAGNOSIS_PREFIX)]

        # Count non-null DIAG and OPER codes
        n_diag = sum(row[diag_cols].notna())

        # Generate all unique combinations of diagnosis codes
        combo_rows = []
        combo_number = 1
        count_new_rows = 0
        count_processed_rows = 0
        if n_diag > 1:
            # Always keep DIAG_01
            diag_01_col = diag_cols[0]
            other_diag_cols = diag_cols[1:]
            # Get indices of non-null diagnosis codes in other_diag_cols
            non_null_other_diag_indices = [i for i, col in enumerate(other_diag_cols) if pd.notna(row[col])]
            n_other_diag = len(non_null_other_diag_indices)
            for r in range(1, n_other_diag + 1):
                for combo in itertools.combinations(non_null_other_diag_indices, r):
                    new_row = row.copy()
                    # Set all DIAG columns except DIAG_01 to NA
                    new_row.loc[other_diag_cols] = pd.NA
                    # Restore DIAG_01
                    new_row.loc[diag_01_col] = row.loc[diag_01_col]
                    # Restore only the columns in this combination (offset by 1 for DIAG_01)
                    keep_cols = [other_diag_cols[idx] for idx in combo]
                    new_row.loc[keep_cols] = row.loc[keep_cols]
                    # Update PROVSPNO with unique combination descriptor
                    new_row['PROVSPNO'] = (
                        f"{row['PROVSPNO']}{DEFAULT_DELIMITER}Combinations{DEFAULT_DELIMITER}{combo_number}"
                    )
                    combo_rows.append(new_row)
                    combo_number += 1
                    count_new_rows += 1
            count_processed_rows += 1
        new_rows.extend(combo_rows)

        return new_rows

    @staticmethod
    def generate_new_rows_vectorized_(df: pd.DataFrame) -> pd.DataFrame:
        """
        Fully vectorized approach using bitmasking to generate all combinations of diagnosis codes for all rows.

        Args:
            df (pd.DataFrame): The original DataFrame.

        Returns:
            pd.DataFrame: DataFrame with all code drop combinations.
        """
        diag_cols = [col for col in df.columns if col.startswith(DIAGNOSIS_PREFIX)]

        # Remove DIAG_01 from diag_df, keep it for later
        diag_01_col = diag_cols[0]
        other_diag_cols = diag_cols[1:]

        # Only operate on secondary diagnosis columns, keep other columns for later merge
        diag_df = df[other_diag_cols].copy()
        other_cols = [col for col in df.columns if col not in diag_cols]

        # Count non-null diagnosis codes per row (excluding DIAG_01)
        row_ns = diag_df.notna().sum(axis=1)
        max_n = row_ns.max()
        if max_n == 0:
            return pd.DataFrame(columns=df.columns)

        # Bitmask cache
        bitmask_cache = {}
        def generate_bitmasks(n, k):
            """
            Recursively generate all bitmasks of length n with k bits set.
            Uses symmetry: bitmasks with k set bits are complements of those with n-k set bits.
            """
            if k < 0 or k > n:
                return []
            if n == 0:
                return [0] if k == 0 else []
            key = (n, k)
            if key in bitmask_cache:
                return bitmask_cache[key]
            if k > n // 2:
                # Use symmetry: invert bitmasks for n-k
                masks = generate_bitmasks(n, n - k)
                full_mask = (1 << n) - 1
                result = [bm ^ full_mask for bm in masks]
                bitmask_cache[key] = result
                return result
            result = []
            # Prepend 0: take all bitmasks of length n-1 with k set bits
            for bm in generate_bitmasks(n-1, k):
                result.append(bm << 1)
            # Prepend 1: take all bitmasks of length n-1 with k-1 set bits
            for bm in generate_bitmasks(n-1, k-1):
                result.append((bm << 1) | 1)
            bitmask_cache[key] = result
            return result

        # Precompute bitmask cache
        for n in range(1, max_n + 1):
            for k in range(1, n + 1):
                bitmask_cache[(n, k)] = generate_bitmasks(n, k)

        all_combinations = []
        # Wrap the outer loop with tqdm for progress bar
        for n in tqdm(range(1, max_n + 1), desc="n (non-null secondary diagnoses)", position=0):
            group = diag_df[row_ns == n]
            if group.empty:
                continue
            # Wrap the k-loop with tqdm for finer progress if desired
            for k in tqdm(range(1, n + 1), desc=f"k (combos for n={n})", leave=False, position=1):
                for bitmask in bitmask_cache[(n, k)]:
                    # Build mask for columns 0 to n-1 (all secondary diagnoses)
                    mask = [(bitmask & (1 << i)) != 0 for i in range(n)]
                    mask_df = pd.DataFrame([mask] * len(group), index=group.index, columns=other_diag_cols[:n])
                    # Prepare new diagnosis columns
                    diag_part = group.copy()
                    diag_part.loc[:, other_diag_cols[:n]] = diag_part.loc[:, other_diag_cols[:n]].where(mask_df, other=pd.NA)
                    if len(other_diag_cols) > n:
                        # Assign pd.NA as a scalar to all remaining columns, after casting to object
                        for col in other_diag_cols[n:]:
                            diag_part[col] = pd.NA
                        diag_part = diag_part.astype({col: 'object' for col in other_diag_cols[n:]})
                    # Add DIAG_01 back
                    diag_part[diag_01_col] = df.loc[diag_part.index, diag_01_col]
                    # Build all columns at once to avoid fragmentation
                    new_data = {}
                    # Diagnosis columns in correct order
                    for col in diag_cols:
                        new_data[col] = diag_part[col] if col in diag_part else df.loc[diag_part.index, col]
                    # Other columns
                    for col in other_cols:
                        new_data[col] = df.loc[diag_part.index, col]
                    # Update PROVSPNO with unique combination descriptor
                    new_data['PROVSPNO'] = (
                        df.loc[diag_part.index, 'PROVSPNO'].astype(str) +
                        f"{DEFAULT_DELIMITER}Combinations{DEFAULT_DELIMITER}{k}"
                    )
                    # Build DataFrame for this combination
                    temp_df = pd.DataFrame(new_data, index=diag_part.index)
                    # Ensure column order matches original
                    temp_df = temp_df[df.columns]
                    all_combinations.append(temp_df)

        if all_combinations:
            return pd.concat(all_combinations, ignore_index=True)

        return pd.DataFrame(columns=df.columns)
