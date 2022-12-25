#!/usr/bin/env python3
"""This Python script takes the raw measurement log files relating to pressure tap measurements, and estimates the
pressures at various locations over time"""

import var_locations
import var_variables
from func_import_export import *
from func_data import *

time_directory = var_locations.time_directory
processed_directory = var_locations.processed_directory
experimental_directory = var_locations.experimental_directory
pressure_input_log = var_locations.pressure_input_log
density_input_log = var_locations.density_input_log
tap_pressures_raw = var_locations.tap_pressures_raw
tap_pressures_smoothed = var_locations.tap_pressures_smoothed
tap_pressures_averaged = var_locations.tap_pressures_averaged

sensor_list = var_variables.sensor_list
time_frames = var_variables.time_frames_tap
time_frame_names = var_variables.time_frame_names_tap
mov_avg = var_variables.moving_average_span_tap
labels = var_variables.labels_tap

channels = np.array([(index, name) for index, name in enumerate(sensor_list) if name is not None])
ch_indices, ch_names = channels[:, 0], channels[:, 1]
create_new_directory(processed_directory)
create_new_directory(experimental_directory)
df_import = combine_pressure_and_density(pressure_input_log, density_input_log, ch_indices, ch_names)
var_to_unit = create_variable_to_unit_dictionary(df_import)
df_std, df_smooth = filter_data_into_time_frames(df_import, time_frames, time_frame_names, mov_avg, labels, ch_names)
df_avg = calculate_time_frame_averages(df_import, df_std, ch_names, time_frame_names, labels)
export_data_csv(df_std, tap_pressures_raw)
export_data_csv(df_smooth, tap_pressures_smoothed)
export_data_csv(df_avg, tap_pressures_averaged)

# end of code
