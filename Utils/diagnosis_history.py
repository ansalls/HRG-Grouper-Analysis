'''
    This module provides utilities for building and managing diagnosis histories.
'''
import os
import pandas as pd
from Utils.constants import (
    DIAGNOSIS_PREFIX, PERSON_ID, DATA_FILE_FOLDER,
    PERSON_TO_SPELLS_FILE, SPELL_ID  # , START_AGE
)
from Utils.cc_codes import get_cc_diags_df, get_comorbidity_codes_df


def get_person_to_spells_map() -> pd.DataFrame:
    '''
        Imports the mapping of person IDs to spells from a CSV file.
    '''
    file_path = os.path.join(DATA_FILE_FOLDER, PERSON_TO_SPELLS_FILE)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    return pd.read_csv(file_path, encoding='utf-8', low_memory=False)


def get_diagnosis_columns(df: pd.DataFrame) -> list[str]:
    '''
        Returns a list of diagnosis column names from the DataFrame.
    '''
    return [col for col in df.columns if col.startswith(DIAGNOSIS_PREFIX)]


def build_diagnosis_history(person_id: str, spells_df: pd.DataFrame) -> pd.DataFrame:
    '''
        Builds diagnosis history for a person with comorbidity and CC list information.
        Returns DataFrame with person_id, diagnosis_code, is_comorbidity, and CC list flags.
    '''
    person_spells = spells_df[spells_df[PERSON_ID] == person_id]
    if person_spells.empty:
        return pd.DataFrame(columns=['person_id', 'diagnosis_code', 'is_comorbidity', 'cc_flags'])

    diag_cols = get_diagnosis_columns(person_spells)
    all_diagnoses = set()
    for _, row in person_spells.iterrows():
        for col in diag_cols:
            if pd.notna(row[col]) and row[col] != '':
                all_diagnoses.add(row[col])

    comorbidity_df = get_comorbidity_codes_df()
    cc_diags_df = get_cc_diags_df()

    history_records = []
    for diag_code in all_diagnoses:
        is_comorbidity = diag_code in comorbidity_df['HRG Format'].values
        cc_flags = {}
        if diag_code in cc_diags_df['CC_Code'].values:
            cc_row = cc_diags_df[cc_diags_df['CC_Code'] == diag_code].iloc[0]
            cc_flags = {col: int(cc_row[col]) for col in cc_diags_df.columns if col != 'CC_Code'}
            if not any(cc_flags.values()):
                continue
        elif not is_comorbidity:
            continue

        history_records.append({
            'person_id': person_id,
            'diagnosis_code': diag_code,
            'is_comorbidity': is_comorbidity,
            'cc_flags': cc_flags
        })

    return pd.DataFrame(history_records)


def process_grouper_output(grouper: pd.DataFrame, person_to_spells: pd.DataFrame) -> pd.DataFrame:
    '''
        Processes grouper output to build diagnosis histories.
    '''
    all_histories = []
    person_id = ''

    for spell_id in person_to_spells[SPELL_ID].dropna().unique():
        # Append PERSON_ID column to grouper based on SPELL_ID matching
        filtered_spells = person_to_spells.loc[person_to_spells[SPELL_ID] == spell_id]
        if not filtered_spells.empty:
            person_id = filtered_spells[PERSON_ID].iloc[0]
        grouper.loc[grouper[SPELL_ID] == spell_id, PERSON_ID] = person_id

    person_history = build_diagnosis_history(person_id, grouper)
    if not person_history.empty:
        all_histories.append(person_history)

    non_empty_histories = [df for df in all_histories if not df.empty]
    if non_empty_histories:
        return pd.concat(
            non_empty_histories,
            ignore_index=True
        )

    return pd.DataFrame(
        columns=[
            'person_id',
            'diagnosis_code',
            'is_comorbidity',
            'cc_flags'
        ]
    )


def export_diagnosis_history(history_df: pd.DataFrame, output_file: str = "") -> None:
    '''
        Exports the diagnosis history to a CSV file.
    '''
    if not output_file:
        output_file = os.path.join(DATA_FILE_FOLDER, "diagnosis_history.csv")

    if not history_df.empty:
        export_df = history_df.copy()
        if 'cc_flags' in export_df.columns:
            cc_flags_expanded = pd.json_normalize(export_df['cc_flags'].tolist())
            export_df = pd.concat([export_df.drop('cc_flags', axis=1), cc_flags_expanded], axis=1)
        export_df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"Diagnosis history exported to: {output_file}")
    else:
        print("No diagnosis history data to export")
