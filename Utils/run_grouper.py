'''
    This module provides a function that generates a new grouper output file
'''
from os import getenv, path
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv
from Utils.command_runner import run_command_and_wait
import Utils.constants as const


def run_grouper(input_file: str,
               definitions_file: Optional[str] = None,
               output_file: Optional[str] = None,
               grouper_exe: Optional[str] = None,
               ) -> str:
    '''
    Runs the grouper executable with the specified data and definitions files.

    :param data_file: The path to the data file to be processed.
    :param definitions_file: The path to the definitions file to be used.
    :param output_file: The path to the output file to be created.
    :param grouper_exe: The path to the grouper executable.
    :return: The path to the output file.
    '''

    if grouper_exe is None:
        load_dotenv()
        grouper_exe = getenv('GROUPER_EXE')
        if grouper_exe is None:
            raise ValueError("Grouping executable not set")

    if input_file is None:
        raise ValueError("data_file not set")
    if path.split(input_file)[0] == '':
        input_file = path.join(const.HRG_INPUT_FILE_FOLDER, input_file)

    if definitions_file is None:
        definitions_file = const.DEFAULT_RDF_FILE
    if path.split(definitions_file)[0] == '':
        definitions_file = path.join(const.DATA_FILE_FOLDER, definitions_file)

    if output_file is None:
        formated_date = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        file_name = path.split(input_file)[1]
        output_file = file_name.replace(
                        const.DEFAULT_FILE_EXTENSION,
                        f"_output_{formated_date}{const.DEFAULT_FILE_EXTENSION}"
                        )

    if path.split(output_file)[0] == '':
        output_file = path.join(const.HRG_OUTPUT_FILE_FOLDER, output_file)

    command = [
        grouper_exe,
        "-i", input_file,
        "-o", output_file,
        "-d", definitions_file,  # RDF file
        "-l", const.APC_GROUPER_ALGORITHM,  # Admitted Patient Care grouping logic
        "-h",  # indicates that the input file has a header row
        "-v"   # Verbose mode
    ]
    success = run_command_and_wait(command, silent=True)
    if success:
        return output_file

    raise RuntimeError("Grouper execution failed")
