'''
Simple file to test running the probes.
'''

from Probes.admit_method import probe_admit_method
from Probes.admit_source import probe_admit_source
from Probes.code_drop import probe_code_drop
from Probes.discharge_destination import probe_discharge_destination
from Probes.discharge_method import probe_discharge_method
from Probes.episode_duration import probe_episode_duration
from Probes.main_specialty import probe_main_specialty
from Probes.patient_classification import probe_patient_classification
from Probes.sex import probe_sex
from Probes.start_age import probe_start_age
from Probes.treatment_function_code import probe_treatment_function_code
from Utils.time_to_run import ttr

if __name__ == '__main__':
    NO_CACHE = False
    time = ttr()
    probe_admit_method(no_cache=NO_CACHE)
    probe_admit_source(no_cache=NO_CACHE)
    probe_code_drop(no_cache=NO_CACHE)
    probe_discharge_destination(no_cache=NO_CACHE)
    probe_discharge_method(no_cache=NO_CACHE)
    probe_episode_duration(no_cache=NO_CACHE)
    probe_main_specialty(no_cache=NO_CACHE)
    probe_patient_classification(no_cache=NO_CACHE)
    probe_sex(no_cache=NO_CACHE)
    probe_start_age(no_cache=NO_CACHE)
    probe_treatment_function_code(no_cache=NO_CACHE)
    _ = ttr(time)
