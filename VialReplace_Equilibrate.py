import os
import time
import json
import pickle
import argparse

import numpy as np

# Import experiment parameters from custom script
from custom_script import EXP_NAME, PUMP_CAL_FILE
from custom_script import EVOLVER_IP, EVOLVER_PORT, OPERATION_MODE
from custom_script import STIR_INITIAL, TEMP_INITIAL

SAVE_PATH = os.path.dirname(os.path.realpath(__file__))
EXP_DIR = os.path.join(SAVE_PATH, EXP_NAME)
OD_CAL_PATH = os.path.join(SAVE_PATH, 'od_cal.json')
OD_RAW_ZERO_PATH =  os.path.join(SAVE_PATH, 'od_raw_zero.json')
TEMP_CAL_PATH = os.path.join(SAVE_PATH, 'temp_cal.json')


def get_options():
    description = 'Watch for OD and temperature measurements from eVOLVER'
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('vial', 
                        type=int,
                        nargs='?',
                        help='Vial number to monitor (0-15)')

    return parser.parse_args()


def read_file(vial, param):
    file_name =  "vial{0}_{1}.txt".format(vial, param)
    file_path = os.path.join(EXP_DIR, param, file_name)
    data = np.genfromtxt(file_path, delimiter=',')
    return data


def equilibrate(vial):
    old_data = np.asarray([])
    count = 0
    while True:
        # Read OD and temperature from file
        vial = options.vial

        od_data = read_file(vial, "OD")
        raw_od_data = read_file(vial, "od_135_raw")

        if od_data[-1,0] not in old_data:
            old_data = np.append(old_data, od_data[-1,0])
            print(f"{od_data[-1,0]} - {od_data[-1,1]:.3f} - {raw_od_data[-1,1]}")

            # Restart count
            count = 0
        else:
            count += 1
            if count > 20:
                print("No new data found for the past minute.")
                print("Please check that the main experiment script is running.")
                exit()

        # Sleep for 3 second
        time.sleep(3)


def save_blank(vial):
    print("Waiting for new OD measurement...")
    time.sleep(21)

    # Get new raw OD (last OD measurement)
    new_raw = read_file(vial, "od_135_raw")[-1, 1]

    # Load OD calibration raw zero
    with open(OD_RAW_ZERO_PATH, 'r') as f:
        od_raw_zero = json.load(f)

    new_delta = od_raw_zero[vial] - new_raw

    # Check if equilibrating file exists
    equilibrated_file = os.path.join(EXP_DIR, "equilibrated.json")

    if os.path.exists(equilibrated_file):
        # Load equilibrated file
        with open(equilibrated_file, 'r') as f:
            equilibrated = json.load(f)
        equilibrated[vial] = new_delta

    else:
        # Create equilibrated file
        equilibrated = {vial: new_delta}
    
    with open(equilibrated_file, 'w') as f:
        json.dump(equilibrated, f, indent=4)


if __name__ == '__main__':
    options = get_options()
    if options.vial is None:
        print('No vial specified')
        print('Usage: python VialReplace_Equilibrate.py <vial_number (0-15)>')
        exit(1)
    
    vial = options.vial

    while True:
        try:
            print(f"Monitoring vial {options.vial}")
            print(f"Press Ctrl+C to stop")
            equilibrate(options.vial)

        except KeyboardInterrupt:
            try:
                resp = input("Has the vial equilibrated? Save OD blank? (y/n)")
                if resp == 'y':
                    save_blank(vial)
                    print("OD blank saved to equilibrated.json")
                    print("Run python VialReplace_Blank.py to continue")
                    break
                
                else:
                    print("Resuming...")
                    continue

            except KeyboardInterrupt:
                print('Second Ctrl-C detected, shutting down')
                exit(1)

