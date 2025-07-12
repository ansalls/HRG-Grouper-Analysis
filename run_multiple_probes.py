'''
    Simple file to run all of the probes and save the results to a file.
'''
import os
from Probes.admit_method import AdmitMethod
from Probes.admit_source import AdmitSource
from Probes.code_drop import CodeDrop
from Probes.discharge_destination import DischargeDestination
from Probes.discharge_method import DischargeMethod
from Probes.episode_duration import EpisodeDuration
from Probes.main_specialty import MainSpecialty
from Probes.patient_classification import PatientClassification
from Probes.sex import Sex
from Probes.start_age import StartAge
from Probes.treatment_function_code import TreatmentFunctionCode
from Probes.probe_base import run_multiple_probes
from Utils.time_to_run import ttr
from Utils.constants import (DATA_FILE_FOLDER,
                             RAW_FILE_FOLDER,
                             SAMPLE_DATA_FILE,
                             BASE_RDF_FILE
                             )


def run_all_probes():
    '''
        Run all probes and save the results to a file.
    '''
    no_cache = True
    input_file = os.path.join(RAW_FILE_FOLDER, SAMPLE_DATA_FILE)
    rdf_file = os.path.join(DATA_FILE_FOLDER, BASE_RDF_FILE)

    # Ensure the data file is present
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Data file not found: {input_file}")

    if not os.path.exists(rdf_file):
        raise FileNotFoundError(f"RDF file not found: {rdf_file}")

     # List of probe classes to run
    probe_classes = [
        AdmitMethod,
        AdmitSource,
        CodeDrop,
        DischargeDestination,
        DischargeMethod,
        EpisodeDuration,
        MainSpecialty,
        PatientClassification,
        Sex,
        StartAge,
        TreatmentFunctionCode
    ]

    # Run all probes together
    run_multiple_probes(probe_classes, no_cache=no_cache, data_file=input_file,
                        rdf_file=rdf_file)


if __name__ == '__main__':
    # Measure the time taken to run all probes
    time = ttr()

    # Run all probes together
    run_all_probes()

    _ = ttr(time)
