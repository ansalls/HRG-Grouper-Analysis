'''
    This script runs data validation on input data before executing probes.
'''
import os
import pandas as pd
from Plugins.data_validator import create_validator
from Probe_classes.sex import Sex
from Probe_classes.admit_source import AdmitSource
from Probe_classes.admit_method import AdmitMethod
from Probe_classes.patient_classification import PatientClassification
from Probe_classes.discharge_destination import DischargeDestination
from Probe_classes.discharge_method import DischargeMethod
from Probe_classes.treatment_function_code import TreatmentFunctionCode
from Probe_classes.main_specialty import MainSpecialty
from Utils.grouper_data_import import load_grouper_input_file
from Utils.constants import (DATA_FILE_FOLDER,
                             RAW_FILE_FOLDER,
                             SAMPLE_DATA_FILE,
                             BASE_RDF_FILE
                             )


def validate_input_data(df: pd.DataFrame, report_mode: bool = True) -> pd.DataFrame:
    '''
        Validate input data against probe class definitions.
    '''

    if report_mode:
        allow_null = False
        action = 'report_only'
    else:
        allow_null = False
        action = 'assign_first'

    # List of validations to apply. These are all required fields for the grouper.
    validations = [
        AdmitSource,
        AdmitMethod,
        DischargeDestination,
        DischargeMethod,
        MainSpecialty,
        PatientClassification,
        Sex,
        TreatmentFunctionCode,
    ]

    for probe_class in validations:
        validator = create_validator(
            probe_class=probe_class,
            allow_null=allow_null,
            action=action
        )

        df = validator.transform(df)

    return df


def run_validation(report_mode: bool = True) -> tuple[str, pd.DataFrame]:
    '''
        Run the probe analysis with data validation as a preprocessing step.
    '''
    input_file = os.path.join(RAW_FILE_FOLDER, SAMPLE_DATA_FILE)
    rdf_file = os.path.join(DATA_FILE_FOLDER, BASE_RDF_FILE)
    validated_file = ''

    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Data file not found: {input_file}")

    if not os.path.exists(rdf_file):
        raise FileNotFoundError(f"RDF file not found: {rdf_file}")

    df = load_grouper_input_file(rdf_file=rdf_file, data_file=input_file)
    df_validated = validate_input_data(df, report_mode=report_mode)

    if not report_mode:
        validated_file = input_file.replace('.csv', '_validated.csv')
        df_validated.to_csv(validated_file, index=False)

    return validated_file, df_validated


if __name__ == '__main__':
    _ = run_validation(report_mode=True)
