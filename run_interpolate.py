#!/usr/bin/env python3
"""This Python script takes a calibration file and artificially increases the calibration
resolution using interpolation based on Delaunay Triangulation"""

from func_import_export import *
from func_classes import *
from func_graphs import *
import var_locations
import var_variables

calibration_data_directory = var_locations.calibration_directory
calibration_input_file = var_locations.calibration_input_file
calibration_figure_directory = var_locations.calibration_figure_directory
interpolation_data_directory = var_locations.interpolation_data_directory
interpolation_figure_directory = var_locations.interpolation_figure_directory

original_size = var_variables.original_size
interp_size = var_variables.interp_size

create_new_directory(calibration_figure_directory)
create_new_directory(interpolation_data_directory)
create_new_directory(interpolation_figure_directory)

df_calib = import_csv_pandas(calibration_input_file)
calculate_total_and_static_pressure(df_calib)
calculate_dimensionless_pressure(df_calib)
interp_grid = PointGrid(df_calib['pitch'], df_calib['yaw'], interp_size)    # instantiate the calibration grid
df_graph_calib = GraphBundle(df_calib['pitch'], df_calib['yaw'])            # instantiate raw graphing data bundle
df_graph_inter = GraphBundle(interp_grid.x_coord, interp_grid.y_coord)      # instantiate interpolated data bundle

df_interpolation = pd.DataFrame()
df_interpolation['yaw'] = interp_grid.xy_interpolated[:, 1]
df_interpolation.columns = pd.MultiIndex.from_product([df_interpolation.columns, ['(deg)']])
df_interpolation['pitch', '(deg)'] = interp_grid.xy_interpolated[:, 0]
name_end_orig = (str("%.2f" % float(original_size)).replace(".", "-"))
name_end_int = (str("%.2f" % float(interp_size)).replace(".", "-"))
df_graph_calib.x_axis_label, df_graph_calib.y_axis_label = str("pitch (deg)"), str("yaw (deg)")
df_graph_inter.x_axis_label, df_graph_inter.y_axis_label = str("pitch (deg)"), str("yaw (deg)")

array_bundle = ['velocity_mag', 'density', 'c_p_total', 'c_p_static']
array_limits = [[None, None], [None, None], [0, 1], [0, 1]]
for arr_name, plot_limits in zip(array_bundle, array_limits):
    array = np.array(df_calib[arr_name])
    df_graph_calib.data_pivot[df_graph_calib.y_index, df_graph_calib.x_index] = array.flatten()
    df_graph_calib.data = df_graph_calib.data_pivot.flatten()
    interpolate_2d_grid(df_graph_calib, df_graph_inter)
    graph_labels(df_graph_calib, arr_name, None)
    graph_labels(df_graph_inter, arr_name, None)
    df_graph_calib.limits, df_graph_inter.limits = plot_limits, plot_limits
    create_heat_map(df_graph_calib, f'{calibration_figure_directory}heat_map_{arr_name}_{name_end_orig}')
    create_heat_map(df_graph_inter, f'{interpolation_figure_directory}heat_map_{arr_name}_{name_end_int}')
    df_interpolation[arr_name, df_graph_inter.bar_unit] = df_graph_inter.data

plot_limits = list([0, 1])
holes = int(np.array(df_calib['holes'])[0])
for hole in range(1, holes + 1, 1):
    arr_name = f'c_p_local_{hole}'
    array = np.array(df_calib[arr_name]).flatten()
    df_graph_calib.data_pivot[df_graph_calib.y_index, df_graph_calib.x_index] = array
    df_graph_calib.data = df_graph_calib.data_pivot.flatten()
    df_graph_calib.limits = plot_limits
    interpolate_2d_grid(df_graph_calib, df_graph_inter)
    graph_labels(df_graph_calib, 'c_p_local', hole)
    graph_labels(df_graph_inter, 'c_p_local', hole)
    create_heat_map(df_graph_calib, f'{calibration_figure_directory}heat_map_{arr_name}_{name_end_orig}')
    create_heat_map(df_graph_inter, f'{interpolation_figure_directory}heat_map_{arr_name}_{name_end_int}')
    df_interpolation[f'c_p_local_{hole}', df_graph_inter.bar_unit] = df_graph_inter.data

dec_name = (str('%.2f' % float(interp_size)).replace('.', '-'))
file_name = f'{interpolation_data_directory}interpolation_{dec_name}.csv'
export_data_csv(df_interpolation, file_name)

# end of code
