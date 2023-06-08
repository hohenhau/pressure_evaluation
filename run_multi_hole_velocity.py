#!/usr/bin/env python3
"""This Python script takes the raw measurement log files relating to a multi-hole probe, and estimates the
experimental velocity components. Printer log locations are also reformatted for ease of access"""

from func_import_export import *
import var_locations
import var_variables

pressure_input_log = var_locations.pressure_input_log
density_input_log = var_locations.density_input_log
printer_input_log = var_locations.printer_input_log
printer_output = var_locations.printer_output
multi_hole_output = var_locations.multi_hole_output
interpolation_file_coarse = var_locations.interpolation_file_coarse
interpolation_file_fine = var_locations.interpolation_file_fine

switch_y_and_z = var_variables.switch_y_and_z
multi_hole_pressure_channels = var_variables.multi_hole_pressure_channels

df_experiment = combine_pressure_and_density(pressure_input_log, density_input_log, multi_hole_pressure_channels)
df_interpolation_coarse = import_csv_pandas(interpolation_file_coarse)
calculate_dimensionless_pressure(df_experiment)
calculate_pitch_and_yaw(df_experiment, df_interpolation_coarse)
df_interpolation_fine = import_csv_pandas(interpolation_file_fine)
enhance_pitch_and_yaw(df_experiment, df_interpolation_fine)  # rerun calculations with initial result on finer grid
calculate_velocity_components(df_experiment, switch_y_and_z)
export_pressure = [f'c_p_local_{hole + 1}' for hole in range(len(multi_hole_pressure_channels))]
exports_velocity = ['velocity_mag', 'velocity_x', 'velocity_y', 'velocity_z', 'closest_match']
exports_additional = ['timestamp', 'epoch', 'time', 'yaw', 'pitch', 'density', 'temperature']
df_export = df_experiment[exports_additional + export_pressure + exports_velocity].copy()
export_data_csv(df_export, multi_hole_output)
if os.path.exists(printer_input_log):
    df_printer = log_printer_to_csv(df_experiment, printer_input_log)
    export_data_csv(df_printer, printer_output)
else:
    print('No input printer coordinate log was found')

# end of code
