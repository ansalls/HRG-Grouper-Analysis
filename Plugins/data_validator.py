'''
    This module provides a data validation plugin that checks whether the columns
    in the DataFrame have acceptable entries for their respective data elements.
'''
from typing import Type, Union, Dict, Any
from enum import Enum
import pandas as pd
from Plugins.base_plugin import BasePlugin
from Probe_classes.probe_proto import Probe


class ValidationAction(Enum):
    '''
        Enumeration of possible actions to take with violating rows.
    '''
    ASSIGN_FIRST = 'assign_first'
    REMOVE_ROW = 'remove_row'
    REPORT_ONLY = 'report_only'


class DataValidationPlugin(BasePlugin):
    '''
        A plugin that validates data elements against their allowed category entries.

        This plugin takes a probe class that defines allowed values, checks whether
        the corresponding column in the DataFrame contains only acceptable entries,
        and takes action based on the specified validation action.
    '''

    def __init__(self,
                 probe_class: Type[Probe],
                 allow_null: bool = True,
                 action: ValidationAction = ValidationAction.REPORT_ONLY):
        '''
            Initialize the validation plugin.
        '''
        self.probe_class = probe_class
        self.allow_null = allow_null
        self.action = action
        self.column_name = probe_class.column_name()
        self.allowed_values = set(probe_class.probe_values())
        self.validation_report = {}

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        '''
            Validate the DataFrame and take appropriate action based on configuration.
        '''
        if self.column_name not in df.columns:
            print(f"Warning: Column '{self.column_name}' not found in DataFrame.")
            return df

        # Identify invalid rows
        invalid_mask = self.get_invalid_mask(df)
        invalid_count = invalid_mask.sum()

        if invalid_count == 0:
            print(f"\nAll values in column '{self.column_name}' are valid.")
            return df

        self.generate_report(df, invalid_mask)

        if self.action == ValidationAction.ASSIGN_FIRST:
            df = self.assign_first_valid(df, invalid_mask)
        elif self.action == ValidationAction.REMOVE_ROW:
            df = self.remove_invalid_rows(df, invalid_mask)
        elif self.action == ValidationAction.REPORT_ONLY:
            self.print_report()

        return df

    def get_invalid_mask(self, df: pd.DataFrame) -> pd.Series:
        '''
            Get a boolean mask identifying invalid rows.
        '''
        column_data = df[self.column_name].astype(str)  # Coerce column data to string
        # Coerce allowed values to string
        allowed_values = {str(value) for value in self.allowed_values}

        if self.allow_null:
            null_mask = column_data.isna()
            # Valid if value is in allowed values OR is null (when nulls are allowed)
            valid_mask = column_data.isin(allowed_values) | null_mask
        else:
            # Valid only if value is in allowed values
            valid_mask = column_data.isin(allowed_values)

        return ~valid_mask

    def generate_report(self, df: pd.DataFrame, invalid_mask: pd.Series) -> None:
        '''
            Generate a detailed validation report.
        '''
        invalid_df = df[invalid_mask]
        invalid_values = invalid_df[self.column_name]

        # Count occurrences of each invalid value
        value_counts = invalid_values.value_counts(dropna=False)

        # Get row numbers (using 1-based indexing)
        row_numbers = (invalid_df.index + 1).tolist()

        total_rows = len(df)
        invalid_count = len(invalid_df)
        occurrence_rate = (invalid_count / total_rows) * 100 if total_rows > 0 else 0

        self.validation_report = {
            'column_name': self.column_name,
            'invalid_count': invalid_count,
            'occurrence_rate': occurrence_rate,
            'invalid_values': value_counts.to_dict(),
            'row_numbers': row_numbers,
            'action_taken': self.action.value
        }

    def print_report(self) -> None:
        '''
            Print the validation report to console.
        '''
        report = self.validation_report

        print("\n===== Data Validation Report =====")
        print(f"Column: {report['column_name']}")
        print(f"Action: {report['action_taken']}")
        print(f"Invalid Rows: {report['invalid_count']:,}")
        print(f"Occurrence Rate: {report['occurrence_rate']:.2f}%")

        if report['invalid_count'] > 0:
            print("Invalid Values Found:")
            for value, count in report['invalid_values'].items():
                print(f"  '{value}': {count} occurrences")

            # Show first 20 row numbers
            row_numbers = report['row_numbers']
            if len(row_numbers) <= 20:
                print(f"Row Numbers with Invalid Values: {row_numbers}")
            else:
                print(f"First 20 Row Numbers with Invalid Values: {row_numbers[:20]}")

    def assign_first_valid(self, df: pd.DataFrame, invalid_mask: pd.Series) -> pd.DataFrame:
        '''
            Assign the first valid value to invalid entries.
        '''
        if not self.allowed_values:
            print(f"Warning: No allowed values found for {self.probe_class.__name__}")
            return df

        first_valid_value = sorted(list(self.allowed_values))[0]
        invalid_count = invalid_mask.sum()

        df.loc[invalid_mask, self.column_name] = first_valid_value

        print(f"Assigned '{first_valid_value}' to {invalid_count} invalid entries in "
              f"'{self.column_name}'"
              )
        self.print_report()

        return df

    def remove_invalid_rows(self, df: pd.DataFrame, invalid_mask: pd.Series) -> pd.DataFrame:
        '''
            Remove rows with invalid entries.
        '''
        invalid_count = invalid_mask.sum()
        df_filtered = df[~invalid_mask].copy()

        print(f"Removed {invalid_count} rows with invalid entries in '{self.column_name}'")
        self.print_report()

        return df_filtered

    def get_validation_report(self) -> Dict[str, Any]:
        '''
            Get the validation report as a dictionary.
        '''
        return self.validation_report.copy() if self.validation_report else {}


def create_validator(probe_class: Type[Probe],
                     allow_null: bool = True,
                     action: Union[ValidationAction, str] = ValidationAction.REPORT_ONLY
                     ) -> DataValidationPlugin:
    '''
        Create a data validation plugin for a specific probe class.
    '''
    if isinstance(action, str):
        action_map = {
            'report_only': ValidationAction.REPORT_ONLY,
            'assign_first': ValidationAction.ASSIGN_FIRST,
            'remove_row': ValidationAction.REMOVE_ROW
        }
        if action not in action_map:
            raise ValueError(
                f"Invalid action '{action}'. Must be one of: {list(action_map.keys())}")
        action = action_map[action]

    return DataValidationPlugin(probe_class, allow_null, action)
