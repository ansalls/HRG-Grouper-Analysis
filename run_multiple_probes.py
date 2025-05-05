'''
Simple file to run all of the probes and save the results to a file.
'''

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

if __name__ == '__main__':
    NO_CACHE = True
    DATA_FILE = "./data/raw/APC_Sample_Test_Data.csv"
    RDF_FILE = "./data/HRG4+_default_APC.rdf"
    time = ttr()

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
    run_multiple_probes(probe_classes, no_cache=NO_CACHE, data_file=DATA_FILE, rdf_file=RDF_FILE, output_rdf=RDF_FILE)
    _ = ttr(time)
