import os
import json
import time
import pickle
import shutil

# Import experiment parameters from custom script
from custom_script import EXP_NAME, PUMP_CAL_FILE
from custom_script import EVOLVER_IP, EVOLVER_PORT, OPERATION_MODE
from custom_script import STIR_INITIAL, TEMP_INITIAL

SAVE_PATH = os.path.dirname(os.path.realpath(__file__))
EXP_DIR = os.path.join(SAVE_PATH, EXP_NAME)

# Load equilibrated.json file
equilibrated_file = os.path.join(EXP_DIR, 'equilibrated.json')
with open(equilibrated_file, 'r') as f:
    equilibrated = json.load(f)

# Load experiment pickle file
original_pickle_file = os.path.join(EXP_DIR, f"{EXP_NAME}.pickle")
with open(original_pickle_file, 'rb') as f:
    expt_variables = pickle.load(f)
    OD_initial = expt_variables[1]
    """
    expt_variables = [start_time, OD_initial, use_raw_blank]
    start_time: Experiment start time since epoch
    OD_initial: Array of values "Raw_cal_0 - Raw_expt_0" for each vial
    use_raw_blank: bool to use raw OD blank method
    """

# Update OD_initial with values from equilibrated.json (new blanks)
for vial, raw_delta in equilibrated.items():
    OD_initial[vial] = raw_delta
    expt_variables[1] = OD_initial

# Copy a backup of the original pickle file, adding a timestamp to the filename
timestamp = time.strftime("%Y%m%d-%H%M%S")
backup_pickle_file = os.path.join(EXP_DIR, f"{EXP_NAME}_{timestamp}.pickle")
shutil.copyfile(original_pickle_file, backup_pickle_file)

# Save updated OD_initial to pickle file
with open(original_pickle_file, 'wb') as f:
    pickle.dump(expt_variables, f)
