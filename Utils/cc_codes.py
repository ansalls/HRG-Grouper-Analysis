'''
    This module provides utility functions for working with CC diagnoses as the various files
    involved in the process of estimating CC scores.
'''

import os
from typing import Optional
import logging
import pandas as pd
from Utils.constants import CC_CODES_FILE_FOLDER, DATA_FILE_FOLDER, COMORBIDITY_CODES_FILE
from Utils.translators import get_cc_file_for_chapter


logging.basicConfig(
    filename='cc_score_analysis.log',
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def get_cc_diags_df() -> pd.DataFrame:
    '''
        Returns a DataFrame containing the CC codes with columns for each chapter.
    '''
    directory = os.path.abspath("./" + CC_CODES_FILE_FOLDER)
    files = os.listdir(directory)
    cc_files = [f for f in files if f.endswith("_cc_list.csv")]

    chapter_names = [file.split("_")[0] for file in cc_files]
    cc_dataframes = []

    for file, chapter in zip(cc_files, chapter_names):
        file_path = os.path.join(directory, file)
        df = pd.read_csv(file_path, encoding='utf-8', low_memory=False, header=None)
        df.columns = ['CC_Code', 'count']
        df[chapter] = 1
        cc_dataframes.append(df[['CC_Code', chapter]])

    if cc_dataframes:
        merged_df = pd.concat(cc_dataframes, ignore_index=True).groupby(
            'CC_Code', as_index=False).sum()
        for chapter in chapter_names:
            if chapter not in merged_df.columns:
                merged_df[chapter] = 0

        chapter_columns = [col for col in merged_df.columns if col != 'CC_Code']
        merged_df[chapter_columns] = merged_df[chapter_columns].astype(int)

        return merged_df

    return pd.DataFrame(columns=['CC_Code'] + chapter_names)


def estimate_score(hrg: str, diagnosis_codes: list[str]) -> int:
    '''
        Estimates the CC score for a given HRG and list of diagnosis codes.
    '''
    score = 0
    bottom_of_range, _ = get_hrg_cc_range(hrg)

    cc_diags_df = get_cc_codes_for_hrg(hrg)
    if cc_diags_df.empty:
        return score

    unique_diagnosis_codes = set(diagnosis_codes)

    for code in unique_diagnosis_codes:
        if code in cc_diags_df['CC_Code'].values:
            score += 1

    # Some unknown set of codes are worth more than 1 point,
    # so adjust the score up if we know we've underestimated and log the details.
    if score < bottom_of_range:
        hrg_chapter = hrg[:2]
        difference = bottom_of_range - score
        codes_found = set(cc_diags_df['CC_Code'].values).intersection(unique_diagnosis_codes)
        logging.info({
            'hrg': hrg,
            'hrg_chapter': hrg_chapter,
            'score': score,
            'bottom_of_range': bottom_of_range,
            'difference': difference,
            'unique_diagnosis_codes': list(unique_diagnosis_codes),
            'codes_found': list(codes_found)
        })
        score = bottom_of_range

    return score


def get_cc_codes_for_hrg(hrg: str) -> pd.DataFrame:
    '''
        Returns a DataFrame of CC codes for a given HRG.
    '''
    hrg_chapter = hrg[:2]
    cc_file = get_cc_file_for_chapter(hrg_chapter)
    cc_df = pd.read_csv(cc_file, encoding='utf-8', low_memory=False, header=None)
    cc_df.columns = ['CC_Code', 'count']

    # The count column is not needed for this context, so we drop it on return
    return cc_df[['CC_Code']]


def get_hrg_cc_range(hrg: str, df: Optional[pd.DataFrame] = None) -> tuple[int, int]:
    '''
        Returns the CC score range of a given HRG.
    '''
    if df is None or df.empty:
        df = get_cc_hrgs_df()

    if hrg not in df['HRG Code'].values:
        return 0, 0

    top_of_range_val = df[df['HRG Code'] == hrg]['Top of Range'].iloc[0]
    bottom_of_range_val = df[df['HRG Code'] == hrg]['Bottom of Range'].iloc[0]

    # Convert to numeric, handling NaN values
    top_of_range = int(pd.to_numeric(top_of_range_val, errors='coerce')
                       ) if pd.notna(top_of_range_val) else 0
    bottom_of_range = int(pd.to_numeric(bottom_of_range_val, errors='coerce')
                          ) if pd.notna(bottom_of_range_val) else 0

    # Max groups only have a bottom of range.
    if top_of_range is None and bottom_of_range is not None:
        top_of_range = bottom_of_range

    return (bottom_of_range, top_of_range)


def get_cc_hrgs_df(input_file: str = '') -> pd.DataFrame:
    '''
        Return a DataFrame containing the CC HRG data
    '''
    if not input_file:
        input_file = os.path.join(DATA_FILE_FOLDER, 'Priority_CC_HRGs_Data_File.csv')

    df = pd.read_csv(input_file, low_memory=False, encoding='utf-8')

    # We don't explicitely have the top of range column, but the right split on the "-" in the
    # range string (e.g. 10 - 13) is the top of range.
    # Renaming it to Top of Range here for readability.
    if 'Right of -' in df.columns:
        df.rename(columns={'Right of -': 'Top of Range'}, inplace=True)

    return df


def points_to_next_level(hrg: str, diagnosis_codes: list[str]) -> int:
    '''
        Finds the next level of CC score for a given HRG.
    '''
    _, top_of_range = get_hrg_cc_range(hrg)
    score = estimate_score(hrg, diagnosis_codes)

    return int(top_of_range - score + 1) if top_of_range > score else 0


def get_hrg_tariff(hrg: str) -> int:
    '''
        Returns the tariff for a given HRG.
    '''
    df = get_cc_hrgs_df()
    if hrg not in df['HRG Code'].values:
        return 0

    tariff = df[df['HRG Code'] == hrg]['Tariff'].iloc[0]
    return int(tariff) if pd.notna(tariff) else 0


def get_next_hrg_code(hrg: str, df: Optional[pd.DataFrame] = None) -> Optional[str]:
    '''
        Returns the HRG code for the next level of CC score for a given HRG.
    '''
    if df is None or df.empty:
        df = get_cc_hrgs_df()

    if hrg not in df['HRG Code'].values:
        return None

    # Get the next level from the DataFrame.
    # next_level_character is the alphabetic character in the last position of the HRG code.
    # Code A22D has a next level of C, for example, and the next HRG resource grouper is A22C.
    next_level_character = df[df['HRG Code'] == hrg]['Next Level'].iloc[0]
    # The Top of Range code will have NA for next_level_character
    if pd.isna(next_level_character) or next_level_character == "NA":
        return None

    return f"{hrg[0:4]}{next_level_character}"


def get_tariff_for_next_level(hrg: str) -> int:
    '''
        Returns the tariff for the next level of CC score for a given HRG.
    '''
    df = get_cc_hrgs_df()
    next_hrg_code = get_next_hrg_code(hrg, df)
    if not next_hrg_code:
        return 0

    return get_hrg_tariff(next_hrg_code)


def get_max_cc_score_in_chapter(chapter: str) -> int:
    '''
        Returns the maximum CC score for a given chapter.
    '''
    df = get_cc_hrgs_df()
    filtered_df = df[df['Chapter'] == chapter]
    if filtered_df.empty:
        return 0

    valid_scores = pd.to_numeric(filtered_df['Top of Range'], errors='coerce').dropna()
    max_score = valid_scores.max()
    if not valid_scores.empty and not pd.isna(max_score):
        return int(max_score)
    return 0


def get_comorbidity_codes_df() -> pd.DataFrame:
    '''
        Imports the comorbidity codes dataset.
    '''
    file_path = os.path.join(DATA_FILE_FOLDER, COMORBIDITY_CODES_FILE)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    return pd.read_csv(file_path, encoding='utf-8', low_memory=False)
