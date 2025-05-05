'''
    This module provides functions for probing the grouper
'''
from os import path
from enum import Enum
import pandas as pd
from Probe_classes.probe import Probe
from Probe_classes.grouper_file_type import GrouperFileType
import Utils.constants as const
from Utils.grouper_df_utils import write_output, apply_plugins
from Utils.grouper_file_columns import parse_definition_file, fce_file_additional_cols
from Utils.grouper_data_import import read_data, get_grouper_output_file_by_type
from Utils.run_grouper import run_grouper
from Plugins.period_strip import PeriodStripPlugin
from Plugins.column_extender import ColumnExtenderPlugin
from Plugins.combination_row import CombinationRowPlugin
from Plugins.only_single_episode_spells import OnlySingleEpisodeSpellsPlugin
from Plugins.procodet_null_filler import ProcodetNullFillerPlugin


def add_probe_rows(probe_cls, df: pd.DataFrame) -> pd.DataFrame:
    '''
    For each row in the given DataFrame, create additional rows for each element
    of the provided class.
    Updates the specified column with the class' valued and appends the class
    name and the value  to the 'PROVSPNO' field to ensure a unique identifier.

    Parameters:
    -----------
    probe_cls: The probe class (Enum, Probe subclass, or custom class with generate_new_rows).
    df : pd.DataFrame
        The original DataFrame to which new rows will be appended.

    Returns:
    --------
    pd.DataFrame
        A new DataFrame containing both the original and the additional rows.
    '''
    new_rows = []

    # Prefer vectorized method if available
    if hasattr(probe_cls, 'generate_new_rows_vectorized'):
        # Should return a DataFrame of new rows
        new_rows_df = probe_cls.generate_new_rows_vectorized(df)
        return pd.concat([df, new_rows_df], ignore_index=True)

    # Handle custom probe classes with generate_new_rows (e.g. code_drop)
    if hasattr(probe_cls, 'generate_new_rows'):
        for _, row in df.iterrows():
            new_rows.extend(probe_cls.generate_new_rows(row))
    else:
        # Set up variables based on probe_cls type
        # Enum type - e.g. admission_method
        if issubclass(probe_cls, Enum):
            column_name = probe_cls.column_name()
            probe_values = [member.value for member in probe_cls]
            value_names = [member.name for member in probe_cls]
            probe_name = probe_cls.__name__

        # Probe class type - e.g. start_age
        elif issubclass(probe_cls, Probe):
            column_name = probe_cls.column_name()
            probe_values = probe_cls.probe_values()
            value_names = [str(value) for value in probe_values]
            probe_name = probe_cls.__name__

        else:
            raise TypeError("probe_cls must be an Enum, a Probe subclass, \
                            or have a generate_new_rows method")

        # Single loop to generate new rows
        for _, row in df.iterrows():
            for value, value_name in zip(probe_values, value_names):
                new_row = row.copy()
                new_row[column_name] = value
                new_row["PROVSPNO"] = (
                    f"{row['PROVSPNO']}{const.DEFAULT_DELIMITER}"
                    f"{probe_name}{const.DEFAULT_DELIMITER}"
                    f"{value_name}"
                )
                new_rows.append(new_row)

    new_rows_df = pd.DataFrame(new_rows, columns=df.columns)
    return pd.concat([df, new_rows_df], ignore_index=True)


def create_base_df(no_cache: bool = False,
                   input_rdf = path.join(const.DATA_FILE_FOLDER, const.BASE_RDF_FILE),
                   data_file = const.SAMPLE_DATA_FILE,
                   output_rdf = None) -> pd.DataFrame:
    '''
    Create a base DataFrame for probing purposes.
    '''
    # Parse the definition file to figure out the delimiter and column info
    if data_file is None:
        data_file = const.SAMPLE_DATA_FILE
    if output_rdf is None:
        output_rdf = path.join(const.DATA_FILE_FOLDER, const.DEFAULT_RDF_FILE)

    data_file_path = path.join(const.RAW_FILE_FOLDER, data_file)
    output_file_path = path.join(const.CACHE_FILE_FOLDER, const.PROBE_BASE_FILE)
    output_delimiter, output_column_mappings = parse_definition_file(output_rdf)

    if not no_cache and path.exists(output_file_path):
        return output_delimiter, read_data(output_file_path,
                                           output_column_mappings,
                                           output_delimiter)

    input_delimiter, input_column_mappings = parse_definition_file(input_rdf)

    # Read in the data
    df = read_data(data_file_path, input_column_mappings, input_delimiter)

    # Create a list of plugins
    plugins = [
        ProcodetNullFillerPlugin(),
        PeriodStripPlugin(),
        ColumnExtenderPlugin(prefix=const.DIAGNOSIS_PREFIX, maximum=const.MAX_DIAG_COLS),
        ColumnExtenderPlugin(prefix=const.PROCEDURE_PREFIX, maximum=const.MAX_OPER_COLS),
        CombinationRowPlugin(),
        OnlySingleEpisodeSpellsPlugin(),
    ]

    # Apply the plugins
    # Note that due to the column extender plugins, these are now in the output_rdf format
    df_transformed = apply_plugins(df, plugins)

    # Write out the file so we don't have to recompute it later
    write_output(df_transformed, output_file_path, output_delimiter)

    return output_delimiter, df_transformed

def run_probe(probe_class, no_cache: bool = False):
    '''
    Run a probe for the given enum class.
    '''
    delimiter, df = create_base_df(no_cache)

    # Add enum rows to the DataFrame
    new_df = add_probe_rows(probe_class, df)
    probe_data_file = get_probe_file_name(probe_class, GrouperFileType.INPUT)
    write_output(new_df, probe_data_file, delimiter)
    # Get the output file name
    grouper_output_base_file = get_probe_file_name(probe_class, GrouperFileType.OUTPUT)
    if not path.exists(grouper_output_base_file) or no_cache:
        #Run the grouper
        _ = run_grouper(probe_data_file, None, grouper_output_base_file)

    processed_df = load_probe_data(probe_class)
    compare_permuted_lines_to_source(processed_df)
    #print(f"The data has been processed and saved to {output_file_path}")

def get_probe_file_name(probe_class, gf_type: GrouperFileType) -> str:
    '''
    Get the output file name for the probe based on the enum class name.
    '''
    if isinstance(probe_class, Enum):
        file_name = f"{probe_class.__name__.lower()}{const.DEFAULT_FILE_EXTENSION}"
    elif isinstance(probe_class, Probe):
        file_name = f"{probe_class.__name__.lower()}{const.DEFAULT_FILE_EXTENSION}"
    else:
        file_name = f"{probe_class}{const.DEFAULT_FILE_EXTENSION}"
    if gf_type == GrouperFileType.INPUT:
        directory = const.HRG_INPUT_FILE_FOLDER
    else:
        directory = const.HRG_OUTPUT_FILE_FOLDER

    file_base = path.join(directory, file_name)

    return get_grouper_output_file_by_type(file_base, gf_type)

def run_multiple_probes(probe_classes: list, no_cache=False, data_file=None, rdf_file = None, output_rdf=None) -> None:
    '''
    Run multiple probes simultaneously and save the comparison results to a file.

    Parameters:
    -----------
    probe_classes : List of probe classes to run.
    no_cache : Bypass caching and recompute the base DataFrame and grouper output.
    '''
    # Create the base DataFrame
    delimiter, df_base = create_base_df(no_cache, data_file=data_file, input_rdf=rdf_file, output_rdf=output_rdf)

    # Generate all probe rows
    probe_rows_list = []
    for probe_cls in probe_classes:
        temp_df = add_probe_rows(probe_cls, df_base)
        # Extract only the new probe rows (exclude base rows)
        new_rows_df = temp_df.iloc[len(df_base):]
        probe_rows_list.append(new_rows_df)

    # Concatenate base DataFrame with all probe rows
    # Note that the probe rows list is a list of dataframes, one per probe class
    df_combined = pd.concat([df_base] + probe_rows_list, ignore_index=True)

    # Write combined DataFrame to input HRG file
    hrg_input_file = get_probe_file_name("multiple_probes",
                                         GrouperFileType.INPUT)
    hrg_output_file = get_probe_file_name("multiple_probes",
                                          GrouperFileType.OUTPUT)
    # this is just adding the class name to the file name, but we've already done that above, right?
    #input_file = get_grouper_output_file_by_type(file_base, GrouperFileType.INPUT)


    write_output(df_combined, hrg_input_file, delimiter)

    # Run grouper on the combined DataFrame
    if not path.exists(hrg_output_file) or no_cache:
        run_grouper(hrg_input_file, None, hrg_output_file)


    grouper_processed_file = get_grouper_output_file_by_type(hrg_output_file, GrouperFileType.FCE)

    # Load grouper output
    definition_file_path = path.join(const.DATA_FILE_FOLDER, const.DEFAULT_RDF_FILE)
    delimiter, column_mappings = parse_definition_file(definition_file_path)
    column_mappings = fce_file_additional_cols(column_mappings)
    df_grouper_output = read_data(grouper_processed_file, column_mappings, delimiter)

    # Perform comparison and collect results
    comparison_df = compare_multiple_probes(df_grouper_output)

    # Save comparison results to a file
    comparison_file = path.join(
        const.PROCESSED_FILE_FOLDER,
        f"multiple_probes_results{const.DEFAULT_FILE_EXTENSION}"
        )

    write_output(comparison_df, comparison_file, delimiter)
    print(f"Comparison results saved to {comparison_file}")

def load_probe_data(probe_class) -> pd.DataFrame:
    '''
    Load a probe DataFrame for the given enum class.
    '''
    base_output_file_path = get_probe_file_name(probe_class, GrouperFileType.OUTPUT)
    output_file_path = get_grouper_output_file_by_type(base_output_file_path, GrouperFileType.FCE)
    definition_file = path.join(const.DATA_FILE_FOLDER, const.DEFAULT_RDF_FILE)
    delimiter, column_mappings = parse_definition_file(definition_file)
    column_mappings = fce_file_additional_cols(column_mappings)
    return read_data(output_file_path, column_mappings, delimiter)


def compare_multiple_probes(df: pd.DataFrame) -> pd.DataFrame:
    '''
    Compare probe rows to their corresponding source rows and collect the results.

    Parameters:
    -----------
    d_output : pd.DataFrame
        The DataFrame containing the grouper output with source and probe rows.
    Returns: pd.DataFrame
    --------
    '''
    source_results = {}

    # First pass: Collect source SpellHRG values
    for _, row in df.iterrows():
        provspno = row["PROVSPNO"]
        if is_source_row(row):
            source_results[provspno] = row["SpellHRG"]

    # Create new columns initialized with NaN
    df["BasePROVSPNO"] = pd.NA
    df["Probe"] = pd.NA
    df["ProbeValue"] = pd.NA
    df["SourceSpellHRG"] = pd.NA
    df["PermutedSpellHRG"] = pd.NA
    df["Match"] = pd.NA

    # Second pass: Update permuted rows with comparison data
    for idx, row in df.iterrows():
        if not is_source_row(row):
            try:
                # Parse probe row PROVSPNO
                base_provspno, probe, probe_value = parse_child_spell(row["PROVSPNO"])
                source_hrg = source_results.get(base_provspno)
                permuted_hrg = row["SpellHRG"]
                match = False if source_hrg is None else (permuted_hrg == source_hrg)

                # Update the row with comparison data
                df.at[idx, "BasePROVSPNO"] = base_provspno
                df.at[idx, "Probe"] = probe
                df.at[idx, "ProbeValue"] = probe_value
                df.at[idx, "SourceSpellHRG"] = source_hrg
                df.at[idx, "PermutedSpellHRG"] = permuted_hrg
                df.at[idx, "Match"] = match
            except ValueError:
                # Skip rows with invalid PROVSPNO, leaving them with NaN values
                continue

    return df


def compare_permuted_lines_to_source(df: pd.DataFrame):
    '''
    Compare permuted lines to the source line in the DataFrame.
    Gets a row from the DataFrame, determines if it's source or permuted,
    and then compares it to the source row.
    '''
    source_results = {}
    child_results = {}
    for _, row in df.iterrows():
        # For every row, create a new row with the permuted column value
        if is_source_row(row):
            source_results.update({row["PROVSPNO"]: row["SpellHRG"]})
        else:
            child_provspno, enum_class, enum_member = parse_child_spell(row["PROVSPNO"])
            count = child_results.get((child_provspno, row["SpellHRG"]), 0) + 1
            child_results.update({(child_provspno, row["SpellHRG"]): count})
            child_results.update({(child_provspno, enum_class, enum_member): row["SpellHRG"]})

    # Let's count the mismatches and display the details.
    mismatch_count = 0

    # Iterate over each key, value pair in child_results.
    for key, child_hrg in child_results.items():
        # We're interested only in keys with 3 pieces for now
        if isinstance(key, tuple) and len(key) == 3:
            child_provspno, enum_class, enum_member = key
            source_hrg = source_results.get(child_provspno)

            if source_hrg is None:
                mismatch_count += 1
                print(f"Mismatch for PROVSPNO {child_provspno} - {enum_class}.{enum_member}: "
                      f"child HRG '{child_hrg}' <> source HRG 'None'")

            elif child_hrg != source_hrg:
                mismatch_count += 1
                print(f"Mismatch for PROVSPNO {child_provspno} - {enum_class}.{enum_member}: "
                      f"child HRG '{child_hrg}' <> source HRG '{source_hrg}'")

    print(f"Total mismatches: {mismatch_count}")


def parse_child_spell(provspno: str) -> tuple[str, str, str] :
    '''
    Parse the child spell from the given PROVSPNO.
    return: original PROVSPNO, enum class name, enum member name
    '''
    parts = provspno.split(const.DEFAULT_DELIMITER)
    if len(parts) != 3:
        raise ValueError(f"Expected 3 parts, got {len(parts)}: {parts}")
    child_provspno, enum_class, enum_member = parts
    return child_provspno, enum_class, enum_member


def is_source_row(row: pd.Series) -> bool:
    '''
    Determine if the given row is a source row.
    Assumes delimiter is not present in source spell PROVSPNO.
    '''
    provspno = row["PROVSPNO"]
    if pd.isna(provspno):
        return True  # Treat NaN as a source row
    return const.DEFAULT_DELIMITER not in provspno
