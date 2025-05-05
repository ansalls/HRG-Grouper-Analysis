'''
    This module provides functions for reading and processing the
    grouper's input and output data files.
'''
from os import path
import pathlib as p
import pandas as pd
from Probe_classes.grouper_file_type import GrouperFileType
from Utils.constants import DEFAULT_FILE_EXTENSION, DEFAULT_RDF_FILE
from Utils.file_utils import file_extension_replace
from Utils.grouper_file_columns import parse_definition_file


def read_data(data_file: p.Path, column_definitions: list, delimiter: str = ',') -> pd.DataFrame:
    '''
    Reads the data file and creates a df using the columns specified.

    Note: columns in the file that are not in column_definitions will be dropped.
    '''
    # Extract the expected display column names in the correct order
    display_names = [column[0] for column in column_definitions]

    drop_extraneous_columns = get_drop_extraneous_columns_function(len(display_names))

    df = pd.read_csv(data_file, delimiter=delimiter, dtype=str,
                     engine='python', on_bad_lines=drop_extraneous_columns,
                     encoding='cp1252')

    # Convert columns to the order specified in the definition file
    df = df.reindex(columns=display_names)

    numeric_columns = ['EPIORDER', 'STARTAGE']
    # Convert columns to the correct types if they exist in the DataFrame
    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], downcast='integer', errors='coerce')

    return df


def drop_columns(df: pd.DataFrame, columns: list) -> None:
    '''
    Drops the specified columns from the DataFrame if they are present.
    '''
    df.drop(columns=columns, errors='ignore', inplace=True)


def drop_unnecessary_columns(df: pd.DataFrame) -> None:
    '''
    Drops columns that are not relevant. Most are relics that are no longer
    populated by the grouper.
    Source: HRG4+ 2024/25 Local Payment Grouper User Manual v1.0
    '''
    columns_to_drop = [
        'ReportingEPIDUR',
        'FCETrimpoint',
        'FCEExcessBeddays',
        'FCESSC_Ct',
        'FCESSCs1',
        'FCESSCs2',
        'FCESSCs3',
        'FCESSCs4',
        'FCESSCs5',
        'FCESSCs6',
        'FCESSCs7',
        'ReportingSpellLOS',
        'SpellTrimpoint',
        'SpellExcessBeddays',
        'SpellSSC_Ct',
        'SpellSSCs1',
        'SpellSSCs2',
        'SpellSSCs3',
        'SpellSSCs4',
        'SpellSSCs5',
        'SpellSSCs6',
        'SpellSSCs7',
        'SpellFlag_Ct',
        'SpellFlag1',
        'SpellFlag2',
        'SpellFlag3',
        'SpellFlag4',
        'SpellFlag5',
        'SpellFlag6',
        'SpellFlag7',
    ]

    drop_columns(df, columns_to_drop)

def load_grouper_input_file(rdf_file: p.Path, data_file: p.Path) -> pd.DataFrame:
    '''
    Loads the data from the specified files and returns a DataFrame.
    '''
    delimiter, column_definitions = parse_definition_file(rdf_file)
    df = read_data(data_file, column_definitions, delimiter)
    #drop_unnecessary_columns(df)
    return df

def get_grouper_output_file_by_type(output_file_base: str, gf_type: GrouperFileType) -> str:
    '''
    Given an output file path and name, return a new path with the file type appended.
    This gets the name for the output file to pass to the grouper, or
    given the name of the output file, can derive the name of a
    specific grouper output file.
    '''
    if not isinstance(gf_type, GrouperFileType):
        raise ValueError("type must be a GrouperFileType member")

    if DEFAULT_FILE_EXTENSION in output_file_base:
        return file_extension_replace(
                output_file_base,
                DEFAULT_FILE_EXTENSION,
                f"{gf_type.value}{DEFAULT_FILE_EXTENSION}"
                )
    return path.join(output_file_base, f"{gf_type.value}{DEFAULT_FILE_EXTENSION}")

def import_zl_data(input_file: str,
                   input_delim: str = ',',
                   def_file = '.\\data\\' + DEFAULT_RDF_FILE) -> pd.DataFrame:
    '''
    Returns a dataframe from the input zl data file that matches the
    definition file provided.

    Due to the size of these files, we need a more optimized input method
    than read_data
    '''
    # Parse the grouper definitions file to get the column names
    definition_delim, column_definitions = parse_definition_file(def_file)
    display_names = [column[0] for column in column_definitions]

    # Read only the header to get the  input column names
    input_header = pd.read_csv(input_file, nrows=0, delimiter=input_delim,
                               encoding='cp1252').columns.tolist()

    # Build a mapping between input file columns and definition columns
    mapping = {}

    for column in display_names:
        # OPTIMIZE: this isn't very efficienct but impact is negligible
        matched = [input_column for input_column in input_header
                   if has_match(column, input_column)]
        if matched:
            mapping[matched[0]] = column

    columns_to_load = list(mapping.keys())
    df = pd.read_csv(input_file, usecols=columns_to_load,
                     delimiter=input_delim, dtype=str,
                     encoding='cp1252')

    # Rename columns to match the definition.
    df.rename(columns=mapping, inplace=True)

    for column in display_names:
        if column not in df.columns:
            raise ValueError(f"Missing column: {column} in input file.")
            # Alternatively, perhaps just add these and fill them with NaN
            #df[column] = np.nan

    # Convert columns to the order specified in the definition file
    df = df.reindex(columns=display_names)

    numeric_columns = ['EPIORDER', 'STARTAGE']
    # Convert columns to the correct types if they exist in the DataFrame
    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], downcast='integer', errors='coerce')

    return definition_delim, df

def has_match(definition_column: str, input_column: str) -> bool:
    """
    Returns True if the input column matches the definition column,
    accounting for:
        - Removal of an "NHS " prefix.
        - DIAG/OPER columns are missing an underscore.
        - "HAR AGE" should map to "STARTAGE".
    """
    # Normalize input column
    norm_input = input_column.upper().replace("NHS ", "").strip()

    if norm_input == definition_column:
        return True

    # Accept both "DIAG_XX" and "DIAGXX"
    elif definition_column.startswith("DIAG_"):
        if norm_input.replace("_", "") == definition_column.replace("_", ""):
            return True

    # Accept both "OPER_XX" and "OPERXX"
    elif definition_column.startswith("OPER_"):
        if norm_input.replace("_", "") == definition_column.replace("_", ""):
            return True

    # Special case - map "HAR AGE" to "STARTAGE"
    elif definition_column == "STARTAGE":
        if norm_input == "HAR AGE":
            return True

    return False

def get_drop_extraneous_columns_function(num_cols = 0):
    '''
        Grouper outputs a variable number of unbundled HRGs, which we
        don't care about, in their own columns, so we drop them.
        If we don't have an explicit number to drop, pass the list back
        to the parser as-is. It'll drop the columns that aren't in the
        header row (with a parser warning).
    '''
    if num_cols > 0:
        def drop_extraneous_columns(bad_line):
            return tuple(bad_line[:num_cols])

    else:
        def drop_extraneous_columns(bad_line):
            return tuple(bad_line)

    return drop_extraneous_columns
