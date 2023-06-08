#!/usr/bin/env python3
"""This Python script takes an raw measurement log files relating to a pitot rake, and estimates the
experimental velocity magnitude"""

from func_import_export import *
from func_classes import *
from func_graphs import *
import var_locations
import var_variables

# Specify file and directory names and base parameters
time_directory = var_locations.time_directory
processed_directory = var_locations.processed_directory
experimental_directory = var_locations.experimental_directory
pitot_rake_input_field = var_locations.pitot_rake_input_field
pitot_rake_input_printer = var_locations.pitot_rake_input_printer
pitot_rake_points = var_locations.pitot_rake_points
pitot_rake_field = var_locations.pitot_rake_field
pitot_rake_offsets = var_variables.pitot_rake_offsets
offset_in_x = var_variables.offset_in_x
flip_x, flip_y = var_variables.flip_x, var_variables.flip_y

no_edges = var_variables.no_edges
no_corners_1, no_corners_3 = var_variables.no_corners_1, var_variables.no_corners_3
pitot_rake_export_field = var_variables.pitot_rake_export_field
pitot_rake_export_average = var_variables.pitot_rake_export_average
pitot_rake_export_graph = var_variables.pitot_rake_export_graph
pitot_rake_export_limits = var_variables.pitot_rake_export_limits
scat, heat, cont = var_variables.pr_scat, var_variables.pr_heat, var_variables.pr_cont

create_new_directory(processed_directory)
create_new_directory(experimental_directory)
df_measurements = import_csv_pandas(pitot_rake_input_field)
df_printer = import_csv_pandas(pitot_rake_input_printer)
if flip_x is True:
    df_printer['probe_x'] = flip_coordinates(np.array(df_printer['probe_x']))
    if offset_in_x:
        pitot_rake_offsets.reverse()
if flip_y is True:
    df_printer['probe_y'] = flip_coordinates(np.array(df_printer['probe_y']))
    if not offset_in_x:
        pitot_rake_offsets.reverse()
probe_x, probe_y = np.array(df_printer['probe_x']), np.array(df_printer['probe_y'])
df_processed = filter_pitot_rake_field(df_measurements, df_printer, pitot_rake_offsets, offset_in_x)
df_field = calculate_average_field_values(df_processed)

df_export = df_processed[pitot_rake_export_field].copy()
export_data_csv(df_export, pitot_rake_points)
df_export = df_field[pitot_rake_export_average].copy()
export_data_csv(df_export, pitot_rake_field)

if no_edges is True or no_corners_1 is True or no_corners_3 is True:
    ignore_indices = find_corner_and_edge_indices(df_printer, no_edges, no_corners_1, no_corners_3)
    df_processed_trimmed = remove_indices_from_measurements(df_processed, ignore_indices)
    df_field_trimmed = calculate_average_field_values(df_processed_trimmed)

df_graph = GraphBundle(np.array(df_processed['probe_x']), np.array(df_processed['probe_y']))
df_graph.normalise = var_variables.pitot_normalise
df_graph.norm_factor = var_variables.pitot_norm_factor
df_graph.normalised_limits = var_variables.pitot_norm_limits
df_graph.x_axis_label, df_graph.y_axis_label = str("horizontal coordinate (mm)"), str("vertical coordinate (mm)")
for array_name, plot_limits in zip(pitot_rake_export_graph, pitot_rake_export_limits):
    if heat is False and scat is False and cont is False:
        break
    array = np.array(df_processed[array_name])
    df_graph.limits = plot_limits
    df_graph.data = np.array(df_processed[array_name]).flatten()
    if df_graph.normalise is True:
        normalise_data(df_graph)
    df_graph.data_pivot[df_graph.y_index, df_graph.x_index] = df_graph.data
    graph_labels(df_graph, array_name, None)
    if heat:
        file_name = str(f'{processed_directory}/{time_directory}/figure_heat_{array_name}_{time_directory}')
        create_heat_map(df_graph, file_name)
    if scat:
        file_name = str(f'{processed_directory}/{time_directory}/figure_scat_{array_name}_{time_directory}')
        create_scatter_plot(df_graph, file_name)
    if cont:
        file_name = str(f'{processed_directory}/{time_directory}/figure_cont_{array_name}_{time_directory}')
        create_contour_plot(df_graph, file_name)

# end of code
