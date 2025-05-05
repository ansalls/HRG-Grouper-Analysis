'''
    This module provides a function that loads an Excel sheet, filters rows based on criteria,
    and returns a dictionary mapping a composite key to the tariff value.
'''
from os import path
from pandas import read_excel, DataFrame
from Probe_classes.admit_method import AdmitMethod
from Probe_classes.patient_classification import PatientClassification
from Utils.kv_store import save_kv_store, load_kv_store
from Utils.constants import (DEFAULT_FYE_TAG,
                             TARIFF_APC_SHEET_NAME_NO_TAG,
                             TARIFF_KV_STORE_FILE_NO_TAG,
                             DATA_FILE_FOLDER,
                             PROCESSED_FILE_FOLDER,
                             HRG_COLUMN_NAME)

def get_tariff_kv_store(input_file = None, fye_tag: str = DEFAULT_FYE_TAG, no_cache=False) -> dict:
    '''
    This function loads the tariff data from an Excel file, filters it, and returns a dictionary
    '''
    if input_file is None:
        excel_filename = path.join(DATA_FILE_FOLDER,
                               f"{fye_tag}_sus_tariff_reference_data_at_240924.xlsx")
    else:
        excel_filename = input_file

    output_file = path.join(PROCESSED_FILE_FOLDER,
                            f"{TARIFF_KV_STORE_FILE_NO_TAG}{fye_tag}.json"
                            )

    if path.exists(output_file) and not no_cache:
        return load_kv_store(output_file)

    # Load and filter the data from the Excel file.
    kv_store = load_and_filter_data(excel_filename, fye_tag)

    # Save the kv store to a JSON file so it can be loaded later without reprocessing.
    save_kv_store(kv_store, output_file)

    return kv_store

def load_and_filter_data(filename: str, fye_tag: str = DEFAULT_FYE_TAG) -> str:
    '''
    Loads an Excel sheet, filters rows based on criteria, and returns a dictionary
    mapping a composite key to the tariff value.

    Args:
        filename (str): Path to the Excel workbook.
        sheet_name (str): The sheet name to load from the workbook.

    Returns:
        dict: A dictionary with keys in the format "[Spell Type]-[Admission Type]-[HRG]"
              and values corresponding to the tariff.
    '''
    # Load the Excel sheet into a DataFrame.
    sheet_name = f"{fye_tag}{TARIFF_APC_SHEET_NAME_NO_TAG}"
    df = read_excel(filename, sheet_name=sheet_name)

    # Filter the DataFrame:
    # 1. Include only rows where 'Spell Type' is "DAY" or "ORD"
    # 2. Exclude rows where 'Short Stay Emergency?' equals "SSEM"
    filtered_df = df[
        (df["Spell Type"].isin(["DAY", "ORD"])) &
        (df["Short Stay Emergency?"] != "SSEM")
    ]

    # Build the dictionary with keys formatted as "[Spell Type]-[Admission Type]-[HRG]-[fye_tag]"
    kv_store = {}
    for _, row in filtered_df.iterrows():
        key = f"{row['Spell Type']}-{row['Admission Type']}-{row['HRG']}-{fye_tag}"
        kv_store[key] = row["Tariff"]

    return kv_store

def tariff_kv_store_format() -> str:
    '''
    This function returns the format of the tariff key-value store
    '''
    return "[Spell Type]-[Admission Type]-[HRG]-[FYE Tag]: Tariff"


def add_tariff_key(df: DataFrame) -> DataFrame:
    '''
    Returns a dataframe with an additional column "TariffKey"
    that holds a tariff lookup key in the format "SpellType-AdmitType-HRG-FYE Tag".

    SpellType is determined from the patient class (1,3,4 -> "ORD", 2 -> "DAY"),
    and AdmitType is determined from the admit method (11,12,13 -> "ELE", else "NON").
    '''

    # Create the tariff lookup key column.
    df['TariffKey'] = df.apply(
        lambda row: f"{get_spell_type(int(row[PatientClassification.column_name()]))}-"
                    f"{get_admit_type(row[AdmitMethod.column_name()])}-"
                    f"{row[HRG_COLUMN_NAME]}-"
                    f"{DEFAULT_FYE_TAG}",
        axis=1
        )

    return df

def get_spell_type(classification_value: int) -> str:
    '''
    Converts a patient classification value to its corresponding spell type.
    '''
    try:
        classification = PatientClassification(classification_value)
    except ValueError as exc:
        raise ValueError(f"Invalid patient classification: {classification_value}") from exc

    return PatientClassification.spell_type(classification)

def get_admit_type(admit_value: str) -> str:
    '''
    Converts an admit method value to its corresponding admit type.
    '''
    try:
        admit_method = AdmitMethod(admit_value)
    except ValueError as exc:
        raise ValueError(f"Invalid admit method: {admit_value}") from exc

    return AdmitMethod.admit_type(admit_method)

def add_tariff_value(df: DataFrame, kv_store: dict) -> DataFrame:
    '''
    Adds a column "TariffValue" to the DataFrame based on the "TariffKey" column.
    The values are looked up from the kv_store dictionary.
    '''
    df["TariffValue"] = None

    # Update the "TariffValue" column based on the "TariffKey" column.
    df["TariffValue"] = df["TariffKey"].map(kv_store)

    return df

def add_tariff_columns(df: DataFrame) -> DataFrame:
    '''
    Adds "TariffKey" and "TariffValue" columns to the DataFrame.
    The "TariffKey" is generated from the patient classification and admit method,
    and the "TariffValue" is looked up from the kv_store.
    '''
    # Add the TariffKey column.
    df = add_tariff_key(df)

    # Get the kv_store.
    kv_store = get_tariff_kv_store()

    # Add the TariffValue column.
    df = add_tariff_value(df, kv_store)

    return df
