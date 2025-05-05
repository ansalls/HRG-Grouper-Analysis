'''
This script is a command line tool that reads a definition file and a data file,
applies a series of data transformation plugins to the data, and outputs the
resulting DataFrame to a new CSV file.
'''
import argparse
from Plugins.only_inpatient_baseclass import OnlyInpatientPlugin
from Plugins.procodet_null_filler import ProcodetNullFillerPlugin
from Plugins.period_strip import PeriodStripPlugin
from Plugins.nc_strip import NcStripPlugin
from Plugins.append_x import AppendXPlugin
from Plugins.column_extender import ColumnExtenderPlugin
from Plugins.combination_row import CombinationRowPlugin
from Plugins.only_single_episode_spells import OnlySingleEpisodeSpellsPlugin
from Plugins.data_stats import DataStatsPlugin
from Utils.file_utils import get_default_output_file
from Utils.grouper_data_import import import_zl_data
from Utils.grouper_df_utils import apply_plugins, write_output
from Utils.time_to_run import ttr
from Utils.constants import (MAX_DIAG_COLS, MAX_OPER_COLS,
                             DIAGNOSIS_PREFIX, PROCEDURE_PREFIX,
                             DEFAULT_RDF_FILE)

def main():
    '''
        This function is the main entry point for the script.
    '''
    parser = argparse.ArgumentParser(
        description="Load data based on a definition file,\
            apply transformations, and output a new CSV."
    )
    parser.add_argument("data_file", help="Data file.")
    parser.add_argument("definition_file", help="Definition file.", default=DEFAULT_RDF_FILE)
    args = parser.parse_args()

    definition_file_path = args.definition_file
    data_file_path = args.data_file
    time = ttr()
    output_file_path = process_zl_data_file(data_file_path, definition_file_path)

    print(f"The data has been processed and saved to {output_file_path}")
    _ = ttr(time)

if __name__ == "__main__":
    main()

def process_zl_data_file(data_file_path: str,
                         definition_file_path = '.\\data\\' + DEFAULT_RDF_FILE
                         ) -> str:
    '''
    This function runs the plugins on the data file and writes the output to a new CSV file.
    Note: DataStatsPlugin prints output to the console.
    '''

    # Read in the data
    definition_delim, df = import_zl_data(data_file_path, '|', definition_file_path)

    # Create a list of plugins
    plugins = [
        OnlyInpatientPlugin(),
        ProcodetNullFillerPlugin(),
        PeriodStripPlugin(),
        NcStripPlugin(),
        AppendXPlugin(),
        ColumnExtenderPlugin(prefix=DIAGNOSIS_PREFIX, maximum=MAX_DIAG_COLS),
        ColumnExtenderPlugin(prefix=PROCEDURE_PREFIX, maximum=MAX_OPER_COLS),
        CombinationRowPlugin(replace_rows=True),
        OnlySingleEpisodeSpellsPlugin(),
        DataStatsPlugin(),
    ]

    # Apply the plugins in sequence
    df_transformed = apply_plugins(df, plugins)

    # Get output file path
    output_file_path = get_default_output_file(data_file_path)

    # Write out the final CSV
    write_output(df_transformed, output_file_path, definition_delim)

    return output_file_path
