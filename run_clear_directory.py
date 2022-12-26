#!/usr/bin/env python3
"""This Python script deletes all files and directories that were created with the other run modules"""

from pathlib import Path
import shutil
import var_locations

print('Are you sure you want to clear the folder? This will delete all generated files... (type \'yes\')')
confirmation = str(input()).strip().lower()
if confirmation != 'yes':
    print('Cancelling...')
    exit()
else:
    print('Deleting files... ')

dir1 = var_locations.processed_directory
dir2 = var_locations.interpolation_data_directory
dir3 = var_locations.interpolation_figure_directory
dir4 = var_locations.calibration_figure_directory
dir5 = '__pycache__'
directories = [dir1, dir2, dir3, dir4, dir5]
for directory in directories:
    try:
        shutil.rmtree(directory)
    except OSError as error:
        print(f'Could not remove {directory}')
        print("Error: %s : %s" % (directory, error.strerror))

measured_directory = var_locations.measured_directory
file1 = 'measured_multi_hole_probe_'
file2 = 'measured_printer_'
files = [file1, file2]
for file in files:
    for f in Path(f'{measured_directory}/').rglob(f'{file}*'):
        try:
            f.unlink()
        except OSError as error:
            print("Error: %s : %s" % (f, error.strerror))

# end of code
