import os
import json
import argparse

parser = argparse.ArgumentParser(description='Update calibration file with corrected OD values')
parser.add_argument('-c', '--cal_file', type=str, required=True, help='Path to calibration file')
parser.add_argument('-n', '--cal_name', type=str, required=True, help='Name of the calibration to update')
parser.add_argument('-l', '--od_list', type=float, required=True, help='List of corrected OD values to update', nargs=16)
args = parser.parse_args()

od_list = args.od_list
if len(od_list) != 16:
	print("List of OD values must have 16 elements")
	exit()

cal_file = args.cal_file
if not os.path.isfile(cal_file):
	print(f"Calibration file {cal_file} not found.")
	exit()

cal_dir = os.path.dirname(cal_file)

cal_name = args.cal_name

j = json.load(open(cal_file, 'r'))

names = []  # Store valid OD calibration names
for c, cal in enumerate(j):  # Iterate over calibrations list
	if cal["calibrationType"] == "od":
		names.append(cal["name"])

		if cal["name"] == cal_name:
			vial_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
			new_order = []
			for v in range(16):
				# Create list of indexes to be used to substitute the original OD values
				# (i.e. the order in which each sleeve measured each calibration OD)
				index_list = vial_list[15+v+1 : v : -1]

				# Take the OD value measured in each go and, for each vial,
				# place it in the position of the OD that eVOLVER think it's measuring

				new_list = [None]*16
				for i, od_value in enumerate(od_list):
					new_list[index_list[i]] = od_value  # Substitute index by OD value

				new_order.append(new_list)

			# Update "measuredData" in original data
			j[c]["measuredData"] = new_order
			break
else:
	print(f'Calibration "{cal_name}" not found. These are the available OD calibrations')
	print(names)
	exit()

json.dump(j, open(os.path.join(cal_dir, 'calibrations.json.out'), 'w'))
print(f'Calibration "{cal_name}" correctly updated')
