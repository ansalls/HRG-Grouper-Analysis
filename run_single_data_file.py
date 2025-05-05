'''
Simple file to test running zl data processing.
'''
from os import path
from Utils.preprocess_raw_data_file import process_zl_data_file
from Utils.time_to_run import ttr
from Utils.run_grouper import run_grouper
from Utils.grouper_file_columns import fce_file_additional_cols, parse_definition_file
from Utils.grouper_data_import import (read_data,
                                       get_grouper_output_file_by_type)
from Utils.grouper_df_utils import write_output
from Utils.constants import (DATA_FILE_FOLDER,
                              DEFAULT_RDF_FILE,
                              PROCESSED_FILE_FOLDER)
from Probe_classes.grouper_file_type import GrouperFileType
from tariff_kv_store import add_tariff_columns


if __name__ == '__main__':
    time = ttr()
    WHICH = ""
    RDF = "Max_OPCS_and_ICD10_Extended.rdf"
    if RDF == "":
        RDF = DEFAULT_RDF_FILE

    if WHICH == "zl":
        INPUT = process_zl_data_file("./data/raw/your_input_data.txt")
    else:
        FILE_NAME = "GA_slim_test_v2"
        FILE_EXTENSION = ".csv"
        INPUT = f"./data/raw/CC_Probes/{FILE_NAME}{FILE_EXTENSION}"

    # Load grouper output
    definition_file_path = path.join(DATA_FILE_FOLDER, RDF)

    # run grouper
    grouper_output = run_grouper(input_file=INPUT, definitions_file=definition_file_path)
    grouper_output_fce = get_grouper_output_file_by_type(grouper_output, GrouperFileType.FCE)
    delimiter, column_mappings = parse_definition_file(definition_file_path)


    # Load grouper output
    definition_file_path = path.join(DATA_FILE_FOLDER, RDF)
    delimiter, column_mappings = parse_definition_file(definition_file_path)
    column_mappings = fce_file_additional_cols(column_mappings)
    df_grouper_output = read_data(grouper_output_fce, column_mappings, delimiter)
    df_processed = add_tariff_columns(df_grouper_output)
    processed_file = path.join(PROCESSED_FILE_FOLDER, f"processed_data_{FILE_NAME}.csv")
    write_output(df_processed, processed_file,",")

    # Print the time taken to run the script
    _ = ttr(time)
