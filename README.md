# eVOLVER Utils Readme

A collection of new python scripts that are notably necessary for optimizing the optical density calibration and replacing vials during an eVOLVER experiment. For reference, see the main manuscript and the full protocol.

## `Cal_inoculation.xlsx`
This Excel sheet allows you to plan an OD calibration by (1) calculating the OD range of the calibration and (2) recalculating the OD of the concentrated culture after measuring the ODs at the end of the calibration, and (3) back-calculating the OD at each calibration step taking into account the OD of the concentrated culture. Using the ODs at each calibration step, you can correct the calibration using the `Cal_correction.py` script.

### Usage

1. Input the calibration information (eVOLVER name, calibration name...) and the OD of the contrentrated culture.

2. Modify the "Volume added" values in the first table to modulate the OD range of the calibration

3. After the calibration procedure, enter the ODs measured for each vial in the "OD after calibration" table, and the sheet will recalculate the OD of the concentrated culture.

4. In the "OD back calculation" table, the ODs at each calibration step will be back-calculated taking into account the OD of the concentrated culture that was calculated in the step above.

5. You can use these ODs to correct the calibration using the `Cal_correction.py` script.


## `Cal_correction.py`

This script reorganises the data of an OD calibration when running the new calibration protocol (fixed vials plus addition of the cells versus rotating vials of 16 different ODs) while using the original calibration software (rotation of 16 concentrations of cells). In addition, it updates the OD values with the list of back-calculated ODs provided by the Excel sheet `Cal_Inoculation.xlsx`.

### Usage

1. Make a new folder.

2. Open a Terminal, navigate to the folder you created, and download the `calibrations.json` file from eVOLVER  using `scp`:
    `scp pi@ip_<address>:evolver/evolver/calibrations.json calibrations.json`.

3. Navigate to the `evolver-utils` folder within the Terminal.

4. Run the `Cal_correction.py` script, providing the 16 back-calculated ODs of each inoculation step.

4. Open the `Cal_correction.py` script and  edit the list `originalOD = [...]` with the back-calculated ODs.

5. Run:

    `python Cal_correction.py -c </path/to/calibrations.json> -n <od_cal_name> -l <OD_0> <OD_1> ... <OD_15>`

    - `/path/to/calibrations.json`: path to the file downloaded in step 2.
    - `od_cal_name`: name of the calibration.
    - `<OD_0> <OD_1> ... <OD_15>`: 16 OD values back-calculated in the Excel file separated by a single space.

    The script will output a new updated calibrations file (`calibrations.json.out`) in the same folder as the original.

6. Finally, upload the updated file to the eVOLVER using `scp`.
    `scp calibrations.json.out pi@<ip_address>:evolver/evolver/calibrations.json`


## `Cal_LEDpower.py`

This script connects to eVOLVER and changes the predefined power of the IR LEDs used for cell density estimation.

### Usage

To set the same LED power in all smart-sleeves:

`python Cal_LEDpower.py -a <ip_address> -p <power>`

- `<ip_address>`: IP of the eVOLVER machine.
- `<power>`: power for all the 16 LEDs. Use 2060 as default.

To set a different LED power for each of the 16 smart-sleeves:

`python Cal_LEDpower.py -a <ip_address> -p <power0> <power1> ... <power15>`

- `<ip_address>`: IP of the eVOLVER machine.
- `<power0>, <power1> … <power15>`: LED power of each sleeve, separated by a single space.


## `Cal_delete.py`

This script allows the user to delete old calibrations from the eVOLVER `calibrations.json` file

### Usage

1. Create a new folder where the `calibrations.json` will be downloaded.

2. Download the `calibrations.json` file from eVOLVER using `scp`:
    `scp pi@ip_<address>:evolver/evolver/calibrations.json calibrations.json`.

3. Run:
    
    `python Cal_delete.py </path/to/calibrations.json> -n <od_cal_name>`

    - `/path/to/calibrations.json`: path to the file downloaded in step 2.
    - `od_cal_name`: name of the calibration.

    The script will overwrite the calibrations file (`calibrations.json`) in the same folder as the original.

4. Upload the updated file to the eVOLVER using `scp`.
    `scp calibrations.json pi@<ip_address>:evolver/evolver/calibrations.json`


## `VialReplace_Equilibrate.py`

This script will:
- Display the calculated OD and raw values for the vial every 20 s.
- Save the equilibrated OD value for the vial in the file equilibrated.json.

### Usage

1. Copy the script into the experiment folder.

2. Run:

    `python VialReplace_Equilibrate.py <vial_number>`

    - `<vial_number>`: number of the vial to be replaced.

3. Slightly rotate the vial and wait for the next measurement. Repeat this until the OD displayed is lower than 0.007.

4. Press `Ctrl+C` to pause the script.

5. The script will prompt: "Has the vial equilibrated? Save OD blank? (y/n)". Press "y" to continue or "n" to repeat step 3.

6. The script will save the equilibrated OD value in the file `equilibrated.json` in the experiment folder.

7. Repeat for other vials if necessary, and then run `VialReplace_Blank.py`.


## `VialReplace_Blank.py`

This script will:
- Make a backup of the `experiment.pickle` file containing the previous OD blank.
- Use the OD value after it is equilibrated (saved in the file `equilibrated.json`) to replace the original blank of the experiment.

### Usage

1. Copy the script into the experiment folder. 

2. Use `VialReplace_Equilibrate.py` to equilibrate the vial and save the equilibrated OD value.

3. Run:

    `python VialReplace_Blank.py`
