#!/usr/bin/env python3
"""This Python script takes the velocity components (and other variables), as measured my a multi-hole probe,
and assigns them to a list of time frames"""

from func_import_export import *
import var_locations
import var_variables

processed_directory = var_locations.processed_directory
experimental_directory = var_locations.experimental_directory
multi_hole_input_points = var_locations.multi_hole_input_points
multi_hole_frames = var_locations.multi_hole_frames
multi_hole_smoothed = var_locations.multi_hole_smoothed
multi_hole_averaged = var_locations.multi_hole_averaged

time_frames = var_variables.time_frames_probe
time_frame_names = var_variables.time_frame_names_probe
mov_avg = var_variables.moving_average_span_probe
labels = var_variables.labels_probe
variables = var_variables.variables_probe

create_new_directory(processed_directory)
create_new_directory(experimental_directory)
df_import = import_csv_pandas(multi_hole_input_points)
df_std, df_smooth = filter_data_into_time_frames(df_import, time_frames, time_frame_names, mov_avg, labels, variables)
df_avg = calculate_time_frame_averages(df_import, df_std, variables, time_frame_names, labels)
export_data_csv(df_std, multi_hole_frames)
export_data_csv(df_smooth, multi_hole_smoothed)
export_data_csv(df_avg, multi_hole_averaged)

# end of code
