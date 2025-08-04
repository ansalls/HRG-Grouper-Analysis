'''
    This module provides utility functions for working with probe classes and DataFrames.
'''
import logging
import pandas as pd
from Probe_classes.probe_proto import Probe

logger = logging.getLogger(__name__)


def translate_probe_values(df: pd.DataFrame,
                           probe_class: Probe,
                           reverse: bool = False
                           ) -> pd.DataFrame:
    '''
        Translates values in a DataFrame column using a probe class.

        Args:
            df: The DataFrame containing the column to translate
            probe_class: The probe class that defines the column and value mappings
            reverse: If True, translates string representations back to coded values.
                    If False, translates coded values to string representations.
    '''
    result_df = df.copy()
    column_name = probe_class.column_name()

    if column_name not in result_df.columns:
        logger.warning("Column '%s' not found in DataFrame. Available columns: %s",
                       column_name, list(result_df.columns))
        return result_df

    if reverse:
        # Create reverse mapping: string names -> coded values
        translation_map = dict(zip(probe_class.probe_value_names(), probe_class.probe_values()))
        operation_desc = "reverse translated"
    else:
        # Create forward mapping: coded values -> string names
        translation_map = dict(zip(probe_class.probe_values(), probe_class.probe_value_names()))
        operation_desc = "translated"

    # Debugging: Log the output of probe_values and probe_value_names
    logger.debug("Probe values: %s", probe_class.probe_values())
    logger.debug("Probe value names: %s", probe_class.probe_value_names())
    logger.debug("Translation map: %s", translation_map)

    # Log unmapped values
    unique_values = result_df[column_name].dropna().unique()
    unmapped_values = set(unique_values) - set(translation_map.keys())
    if unmapped_values:
        value_type = "string values" if reverse else "values"
        logger.warning("Found unmapped %s in column '%s': %s",
                       value_type, column_name, sorted(unmapped_values))
        logger.debug("Translation map keys: %s", sorted(translation_map.keys()))
        logger.debug("Translation map values: %s", sorted(translation_map.values()))

    # Translate the values
    result_df[column_name] = result_df[column_name].map(
        translation_map).fillna(result_df[column_name])

    # Convert to string type for forward translation
    if not reverse:
        result_df[column_name] = result_df[column_name].astype(str)

    logger.info("%s %d values in column '%s'. Unmapped values: %d",
                operation_desc.title(),
                len(translation_map),
                column_name,
                len(unmapped_values)
                )

    return result_df


def translate_multiple_probe_columns(df: pd.DataFrame,
                                     probe_classes: list[Probe],
                                     reverse: bool = False
                                     ) -> pd.DataFrame:
    '''
        Translates multiple probe columns in a DataFrame using their respective probe classes.

        Args:
            df: The DataFrame containing columns to translate
            probe_classes: List of probe classes to apply
            reverse: If True, translates string representations back to coded values.
                    If False, translates coded values to string representations.
    '''
    result_df = df.copy()
    for probe_class in probe_classes:
        result_df = translate_probe_values(result_df, probe_class, reverse=reverse)

    return result_df
