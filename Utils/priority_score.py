'''
    This module provides utility functions for calculating a priority score
'''
import os
import logging
import random
from typing import Optional
from collections import OrderedDict
import pandas as pd
from Utils.constants import (HRG_COLUMN_NAME, SPELL_ID, PERSON_ID, DIAGNOSIS_PREFIX)
from Utils.cc_codes import (get_cc_codes_for_hrg, get_hrg_cc_range, estimate_score,
                            points_to_next_level, get_hrg_tariff, get_tariff_for_next_level,
                            get_cc_hrgs_df, get_next_hrg_code)
from Utils.diagnosis_history import get_person_to_spells_map, build_diagnosis_history
from Utils.run_grouper import run_grouper


def lookup_person_id(spell_id: str, person_to_spells_df: pd.DataFrame) -> Optional[str]:
    '''
        Look up person ID for a given spell ID.
    '''
    matching_rows = person_to_spells_df[person_to_spells_df[SPELL_ID] == spell_id]
    if matching_rows.empty:
        logging.warning("Person ID not found for spell ID: %s", spell_id)
        return None
    return matching_rows[PERSON_ID].iloc[0]


def get_hrg_info(row: pd.Series) -> tuple[str, str]:
    '''
        Extract HRG code and chapter from a grouper data row.
    '''
    hrg_code = row[HRG_COLUMN_NAME]
    hrg_chapter = hrg_code[:2] if hrg_code else ""
    return hrg_code, hrg_chapter


def is_hrg_significant(hrg_code: str) -> bool:
    '''
        Check if HRG code is in our significant list.

        List inclusion criteria:
        - HRG code has a CC component
        - An HRG code sharing the same root appeared at least 5 times in the dataset
        - The HRG codes in the root all have a national tariff value
        - There is a level difference with a value greater than 100 gbp (2024 tariff rate)
    '''
    if not hrg_code:
        return False

    cc_hrgs_df = get_cc_hrgs_df()
    return hrg_code in cc_hrgs_df['HRG Code'].values


def get_spell_diagnosis_codes(row: pd.Series) -> list[str]:
    '''
        Extract diagnosis codes from a spell row, filtering out empty values and duplicates.
    '''
    diag_cols = [col for col in row.index if col.startswith(DIAGNOSIS_PREFIX)]
    diagnosis_codes = []

    for col in diag_cols:
        try:
            value = row.loc[col]
            if pd.notna(value) and str(value).strip() != '':
                diagnosis_codes.append(str(value))
        except (KeyError, IndexError, AttributeError):
            logging.info("Issue accessing diagnosis column %s in row: %s", col, row.name)
            continue

    return list(OrderedDict.fromkeys(diagnosis_codes))


def add_random_cc_codes(existing_diagnoses: list[str],
                        hrg_code: str,
                        count_to_add: int
                        ) -> tuple[list[str], int]:
    '''
        Add random CC codes for the HRG chapter to the existing diagnosis list.
        Returns updated diagnosis list and count of codes added.
    '''
    cc_codes_df = get_cc_codes_for_hrg(hrg_code)
    if cc_codes_df.empty:
        return existing_diagnoses.copy(), 0

    available_codes = [code for code in cc_codes_df['CC_Code'].tolist()
                       if code not in existing_diagnoses]

    if not available_codes:
        return existing_diagnoses.copy(), 0

    if count_to_add >= len(available_codes):
        updated_diagnoses = existing_diagnoses + available_codes
        return updated_diagnoses, len(available_codes)

    codes_to_add = min(count_to_add, len(available_codes))
    selected_codes = random.sample(available_codes, codes_to_add)
    updated_diagnoses = existing_diagnoses + selected_codes
    return updated_diagnoses, codes_to_add


def verify_cc_gaps(input_df: pd.DataFrame,
                   output_file: Optional[str] = None
                   ) -> pd.DataFrame:
    '''
        Run grouper on test data and verify CC gaps.
        Returns DataFrame with verified gap information.
    '''
    if input_df.empty:
        return pd.DataFrame()

    # Save test data to temporary file
    temp_input = "temp_cc_test_input.csv"
    input_df.to_csv(temp_input, index=False)

    try:
        # Run grouper
        grouper_output_file = run_grouper(temp_input, output_file=output_file)
        output_df = pd.read_csv(grouper_output_file)

        # Parse results
        verified_results = []
        for _, row in output_df.iterrows():
            spell_parts = str(row[SPELL_ID]).split('|')
            if len(spell_parts) == 6:
                (original_spell_id, initial_hrg, expected_hrg, current_score,
                 est_gap, count_added_cc_codes) = spell_parts

                computed_hrg = row[HRG_COLUMN_NAME]

                verified_results.append({
                    'original_spell_id': original_spell_id,
                    'initial_hrg': initial_hrg,
                    'expected_hrg': expected_hrg,
                    'computed_hrg': computed_hrg,
                    'current_score': int(current_score),
                    'estimated_gap': int(est_gap),
                    'cc_codes_added': int(count_added_cc_codes),
                    'gap_verified': computed_hrg == expected_hrg and est_gap == count_added_cc_codes
                })

        return pd.DataFrame(verified_results)

    finally:
        if os.path.exists(temp_input):
            os.remove(temp_input)


def get_unused_cc_codes_from_history(person_id: str,
                                     hrg_code: str,
                                     current_diagnoses: list[str],
                                     spells_df: pd.DataFrame
                                     ) -> list[str]:
    '''
        Get list of CC codes from a person's history that aren't already used
    '''
    if not person_id:
        return []

    # Works for now but should use a cached history
    person_history_df = build_diagnosis_history(person_id, spells_df)
    if person_history_df.empty:
        return []

    cc_codes_df = get_cc_codes_for_hrg(hrg_code)
    if cc_codes_df.empty:
        return []

    # Find diagnoses in history that are CC codes for this HRG
    cc_codes_set = set(cc_codes_df['CC_Code'].tolist())
    current_diagnoses_set = set(current_diagnoses)

    person_cc_codes = set()
    for _, hist_row in person_history_df.iterrows():
        if (hist_row['is_comorbidity'] and
            hist_row['diagnosis_code'] in cc_codes_set and
                hist_row['diagnosis_code'] not in current_diagnoses_set):
            person_cc_codes.add(hist_row['diagnosis_code'])

    return list(person_cc_codes)


def calculate_priority_score(row: pd.Series,
                             person_to_spells_df: pd.DataFrame,
                             spells_df: pd.DataFrame,
                             verified_gaps: Optional[pd.DataFrame] = None
                             ) -> float:
    '''
        Calculate priority score for a spell based on HRG, diagnoses, and diagnosis history.
    '''
    hrg_code, _ = get_hrg_info(row)

    if not is_hrg_significant(hrg_code):
        return 0.0

    spell_id = row[SPELL_ID]
    person_id = lookup_person_id(spell_id, person_to_spells_df)

    current_diagnoses = list(get_spell_diagnosis_codes(row))

    verified_gap = 0
    if verified_gaps is not None and not verified_gaps.empty:
        verified_row = verified_gaps[verified_gaps['original_spell_id'] == spell_id]
        if not verified_row.empty:
            verified = verified_row['gap_verified'].iloc[0]
            if verified:
                verified_gap = verified_row['cc_codes_added'].iloc[0]
            if not verified:
                logging.warning(
                    "Spell %s has an unverified gap, using estimated gap instead.", spell_id)
                verified_gap = verified_row['estimated_gap'].iloc[0]

    if verified_gap <= 0:
        logging.info("No gap for spell %s.", spell_id)
        return 0.0

    current_tariff = get_hrg_tariff(hrg_code)
    next_level_tariff = get_tariff_for_next_level(hrg_code)
    tariff_dif = next_level_tariff - current_tariff if next_level_tariff > current_tariff else 0

    if tariff_dif <= 0:
        return 0.0

    unused_hx_cc_codes = get_unused_cc_codes_from_history(person_id or "",
                                                          hrg_code,
                                                          current_diagnoses,
                                                          spells_df)
    count_unused_hx_cc_codes = len(unused_hx_cc_codes)

    # Score = ((1 / verified_gap) * tariff_factor) * (count_unused_hx_cc_codes / verified_gap)
    if verified_gap > 0:
        gap_factor = 1.0 / verified_gap
        tariff_factor = tariff_dif
        history_factor = count_unused_hx_cc_codes / verified_gap
        priority_score = gap_factor * tariff_factor * history_factor
    else:
        priority_score = 0.0

    return priority_score


def calculate_priority_scores(input_grouper_df: pd.DataFrame,
                              person_to_spells_df: Optional[pd.DataFrame] = None,
                              verify_gaps: bool = False
                              ) -> pd.DataFrame:
    '''
        Calculate priority scores for all rows in a grouper DataFrame.
    '''
    if person_to_spells_df is None:
        person_to_spells_df = get_person_to_spells_map()

    verified_gaps = None
    if verify_gaps:
        verification_file = generate_hrg_upgrade_verification_file(input_grouper_df)
        if not verification_file.empty:
            verified_gaps = verify_cc_gaps(verification_file)

    input_grouper_df['PriorityScore'] = input_grouper_df.apply(
        lambda row: calculate_priority_score(
            row, person_to_spells_df, input_grouper_df, verified_gaps),
        axis=1
    )

    return input_grouper_df


def generate_hrg_upgrade_verification_file(grouper_df: pd.DataFrame) -> pd.DataFrame:
    '''
        Create verification data file by adding CC codes to spells and tracking expected results.
    '''
    input_data = []

    for _, row in grouper_df.iterrows():
        initial_hrg, _ = get_hrg_info(row)

        if not is_hrg_significant(initial_hrg):
            continue

        original_diagnoses = list(get_spell_diagnosis_codes(row))
        bottom_range, top_range = get_hrg_cc_range(initial_hrg)
        total_gap = top_range - bottom_range

        if total_gap <= 0:
            continue

        current_score = estimate_score(initial_hrg, original_diagnoses)
        est_gap = points_to_next_level(initial_hrg, original_diagnoses)
        expected_hrg = get_next_hrg_code(initial_hrg)

        # We'll be adding 1 to total_gap number of CCs to ensure we cover the gap if underestimated
        for cc_count in range(1, total_gap + 1):
            updated_diagnoses, count_added_cc_codes = add_random_cc_codes(
                original_diagnoses, initial_hrg, cc_count
            )

            if count_added_cc_codes > 0:
                # Add tracking info to the SPELL_ID field (similar to probes)
                new_spell_id = f"{row[SPELL_ID]}|{initial_hrg}|{expected_hrg}|" \
                    f"{current_score}|{est_gap}|{count_added_cc_codes}"
                new_row = row.copy()
                new_row[SPELL_ID] = new_spell_id

                # Update diagnosis columns.
                # Clear only columns to the right of the set codes until an empty cell is found.
                diag_cols = [col for col in new_row.index if col.startswith(DIAGNOSIS_PREFIX)]
                i = 0
                for i, diag in enumerate(list(dict.fromkeys(updated_diagnoses))):
                    if i < len(diag_cols):
                        new_row[diag_cols[i]] = diag

                # Surely there's a better way to do this, but this will work for now.
                for j in range(i + 1, len(diag_cols)):
                    if pd.isna(new_row[diag_cols[j]]).all() or \
                            str(new_row[diag_cols[j]]).strip() == '':
                        break
                    new_row[diag_cols[j]] = ''

                input_data.append(new_row)

    return pd.DataFrame(input_data) if input_data else pd.DataFrame()
