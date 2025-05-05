'''
    This module provides a function that generates a new output file
    path based on the input file path.
'''
from os import path
from re import match, escape, sub
import pandas as pd
import logging
from typing import List, Optional
from Utils.constants import VERSION_PREFIX


def get_default_output_file(input_file: str, output_file_name: str = None) -> str:
    '''
    Given a file path (e.g. '/path/dir/name.csv' or '/path/dir/name_v3.csv'),
    return a new path that increments the version number.

    If no version suffix is found, we start at '_v2'.
    Args:
        input_file (str): The input file name and path.
        output_file_name (str): The desired output file name (only).
    '''
    directory, input_filename = path.split(input_file)

    if output_file_name is not None:
        return path.join(directory, output_file_name)

    output_file_name = input_filename

    name, ext = path.splitext(output_file_name)

    # Regex to find suffix like _v2, _v10, etc.
    pattern = r'(.*)' + escape(VERSION_PREFIX) + r'(\d+)$'
    version_suffix = match(pattern, name)

    if version_suffix:
        base_name = version_suffix.group(1)
        new_version = int(version_suffix.group(2)) + 1
        return path.join(directory,
                         filename_constructor(base_name,
                                              VERSION_PREFIX,
                                              new_version,
                                              ext)
                                              )

    return path.join(directory, filename_constructor(name, VERSION_PREFIX, 2, ext))

def filename_constructor(base_name: str, version_prefix: str, version_num: int, ext: str) -> str:
    '''
    Given a base name, version prefix, version number, and extension, return a new filename.
    '''
    return f"{base_name}{version_prefix}{version_num}{ext}"

def file_extension_replace(filename, old_ext, new_ext):
    '''
    Given a filename, an old extension, and a new extension, return a new filename
    with the old extension replaced by the new extension.
    '''
    return sub(rf"{old_ext}$", new_ext, filename)

def convert_doubles_to_integers(
    input_file: str,
    columns_to_convert: List[str],
    output_file: Optional[str] = None,
    chunk_size: int = 500000,
    log_frequency: int = 100000
) -> str:
    """
    Convert specified columns in a large CSV file from doubles to integers.
    Processes the file in chunks to minimize memory usage.

    Args:
        input_file (str): Path to the input CSV file.
        columns_to_convert (List[str]): List of column names to convert from double to int.
        output_file (Optional[str]): Path to save the processed file. If None, a default name is generated.
        chunk_size (int): Number of rows to process at once.
        log_frequency (int): How often to log progress (number of rows).

    Returns:
        str: Path to the output file.
    """
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    # Generate default output file name if not provided
    if output_file is None:
        output_file = get_default_output_file(input_file)

    logger.info("Converting columns %s from double to integer", columns_to_convert)
    logger.info("Input file: %s", input_file)
    logger.info("Output file: %s", output_file)

    # Process the CSV in chunks
    total_rows = 0

    # Create iterator for reading chunks - use string dtype to preserve original format of non-specified columns
    chunks = pd.read_csv(input_file, chunksize=chunk_size, dtype=str)

    for i, chunk in enumerate(chunks):
        # Convert specified columns from double to int
        for col in columns_to_convert:
            if col in chunk.columns:
                # Convert to Int64 (pandas nullable integer type) which supports NA values
                chunk[col] = pd.to_numeric(chunk[col], errors='coerce').astype('Int64')
            else:
                logger.warning("Column '%s' not found in CSV", col)

        # Write to output file - first chunk with header, rest without
        mode = 'w' if i == 0 else 'a'
        header = i == 0
        chunk.to_csv(output_file, mode=mode, index=False, header=header)

        # Update row count and log progress
        total_rows += len(chunk)
        if total_rows % log_frequency == 0:
            logger.log(logging.INFO, "Processed %s rows", f"{total_rows:,}")

    logger.log(logging.INFO, "Conversion complete. Total rows processed: %s", f"{total_rows:,}")
    return output_file
