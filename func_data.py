"""This Python module contains a set of functions related to processing data measured by a range of pressure
sensing devices"""

from scipy.interpolate import interp2d
from sklearn.neighbors import BallTree
from scipy.spatial import cKDTree
import pandas as pd
import numpy as np
import datetime


def interpolate_2d_grid(graph_bundle_raw, graph_data_interp):  # interpolation data using Delaunay triangulation
    x_in = graph_bundle_raw.unique_x
    y_in = graph_bundle_raw.unique_y
    z_in = graph_bundle_raw.data_pivot
    interpolation = interp2d(x_in, y_in, z_in, kind='cubic')
    x_out = graph_data_interp.unique_x
    y_out = graph_data_interp.unique_y
    graph_data_interp.data_pivot = interpolation(x_out, y_out)
    graph_data_interp.data = graph_data_interp.data_pivot.flatten()
    return None


def epoch_to_timestamp(epoch):
    utc_time = datetime.datetime.fromtimestamp(epoch, tz=datetime.timezone.utc)
    time_format = '%d/%m/%Y %H:%M:%S.%f'
    datetime_str = utc_time.strftime(time_format)[:-3]
    return datetime_str


def timestamp_to_epoch(timestamp, time_format):
    utc_time = datetime.datetime.strptime(timestamp, time_format)
    epoch = (utc_time - datetime.datetime(1970, 1, 1)).total_seconds()
    return epoch


def flip_coordinates(coordinates):
    max_coordinate = max(coordinates)
    min_coordinate = min(coordinates)
    range_coordinates = max_coordinate - min_coordinate
    coordinates = (coordinates * -1) + 2 * min_coordinate + range_coordinates
    return coordinates


def calculate_total_and_static_pressure(data_frame):
    print('calculating dynamic, static and total pressure')
    velocity_mag = np.array(data_frame['velocity_mag']).astype(float)
    density = np.array(data_frame['density']).astype(float)
    pressure_dynamic = 0.5 * density * velocity_mag ** 2
    pressure_static = np.zeros((data_frame.shape[0], 1), dtype=float)
    pressure_total = pressure_dynamic + pressure_static
    data_frame['pressure_dynamic', '(Pa)'] = pressure_dynamic
    data_frame['pressure_static', '(Pa)'] = pressure_static
    data_frame['pressure_total', '(Pa)'] = pressure_total


def calculate_dimensionless_pressure(data_frame):
    print("finding relevant pressure column indices")
    pressure_labels = []
    coefficient_labels = []
    for index, headings in enumerate(list(data_frame.columns)):
        if headings[1] == '(Pa)' and headings[0][-1].isnumeric():
            pressure_labels.append(headings[0])
        if 'c_p_local' in headings[0]:
            coefficient_labels.append(headings[0])
    n_holes = max(len(pressure_labels), len(coefficient_labels))
    data_frame['holes', '(qty)'] = np.zeros((data_frame.shape[0], 1), dtype=float) + n_holes

    print("calculating dimensionless local pressure coefficients")
    c_p_locals = np.array(data_frame[pressure_labels]).astype(float)
    max_pressure = np.transpose([np.amax(c_p_locals, axis=1)])                  # maximum pressure at each hole
    min_pressure = np.transpose([np.amin(c_p_locals, axis=1)])                  # minimum pressure at each hole
    pressure_range = max_pressure - min_pressure                                # the range of pressures measured
    data_frame['pressure_range', '(Pa)'] = pressure_range
    normal_max = max_pressure / pressure_range                                  # normalised maximum value
    c_p_locals = np.transpose(-c_p_locals / pressure_range + normal_max)        # local pres. coefficients
    for hole, column in enumerate(c_p_locals, start=1):
        data_frame[f'c_p_local_{hole}', '(ratio)'] = column
    if 'pressure_total' in data_frame.columns:
        print("calculating dimensionless total and static pressure coefficients")
        pressure_static = 0
        pressure_total = np.array(data_frame['pressure_total']).astype(float)
        data_frame['c_p_total', '(ratio)'] = (max_pressure - pressure_total) / pressure_range
        data_frame['c_p_static', '(ratio)'] = (min_pressure - pressure_static) / pressure_range

    temporary_list = list()
    for count, old_column in enumerate(pressure_labels, start=1):
        new_column = f'temporary{count}'
        temporary_list.append(new_column)
        data_frame.rename(columns={old_column: new_column}, inplace=True)
    for count, old_column in enumerate(temporary_list, start=1):
        new_column = f'P{count}'
        data_frame.rename(columns={old_column: new_column}, inplace=True)


def closest_match_euclidean(value, lookup_table):  # fastest after testing other matching functions below
    match_array = np.sum((value - lookup_table) ** 2, axis=1)
    closest_match_idx = np.argmin(match_array)
    closest_match_val = match_array[closest_match_idx]
    return closest_match_idx, closest_match_val


def closest_match_gpt(value, lookup_table):
    min_distance = float('inf')
    closest_entry, closest_index = None, None
    for index, entry in enumerate(lookup_table):
        distance = np.linalg.norm(value - entry)
        if distance < min_distance:
            min_distance = distance
            closest_index = index
            closest_entry = entry
    return closest_index, closest_entry


def closest_match_kd_tree(value, lookup_table):
    tree = cKDTree(lookup_table)
    _, closest_index = tree.query(value)
    closest_entry = lookup_table[closest_index]
    return closest_index, closest_entry


def closest_match_ball_tree(value, lookup_table):
    tree = BallTree(lookup_table)
    _, closest_index = tree.query([value])
    closest_entry = lookup_table[closest_index[0]]
    return closest_index, closest_entry


def calculate_pitch_and_yaw(df_experiment, df_interpolation):
    resolution_pitch = abs(df_interpolation['pitch'].iat[1, 0]-df_interpolation['pitch'].iat[2, 0])
    resolution_yaw = abs(df_interpolation['yaw'].iat[1, 0] - df_interpolation['yaw'].iat[2, 0])
    resolution = max(resolution_pitch, resolution_yaw)
    df_experiment['resolution', '(deg)'] = np.zeros((df_experiment.shape[0], 1), dtype=float) + resolution
    print(f"interpolation resolution is {resolution}")

    print("determining pitch (alpha) and yaw (beta) of measured parameters")
    c_p_labels = []
    for index, headings in enumerate(list(df_experiment.columns)):
        if 'c_p_local' in headings[0]:
            c_p_labels.append(headings[0])
    n_measurements = df_experiment.shape[0]
    c_p_experiment = np.array(df_experiment[c_p_labels]).astype(float)
    c_p_interpolation = np.array(df_interpolation[c_p_labels]).astype(float)
    c_p_total, c_p_static = np.array(list()), np.array(list())
    yaw, pitch = np.array(list()), np.array(list())
    closest_match = np.array(list())

    interpolation_c_p_static = np.array(df_interpolation['c_p_static'])
    interpolation_c_p_total = np.array(df_interpolation['c_p_total'])
    interpolation_pitch = np.array(df_interpolation['pitch'])
    interpolation_yaw = np.array(df_interpolation['yaw'])

    for index, c_p_point in enumerate(c_p_experiment, start=1):
        closest_match_idx, closest_match_val = closest_match_ball_tree(c_p_point, c_p_interpolation)
        c_p_static = np.append(c_p_static, interpolation_c_p_static[closest_match_idx])
        c_p_total = np.append(c_p_total, interpolation_c_p_total[closest_match_idx])
        pitch = np.append(pitch, interpolation_pitch[closest_match_idx])
        yaw = np.append(yaw, interpolation_yaw[closest_match_idx])
        closest_match = np.append(closest_match, closest_match_val)
        print(f"finding point {index} of {n_measurements}")

    df_experiment['pitch', '(deg)'] = pitch
    df_experiment['yaw', '(deg)'] = yaw
    df_experiment['c_p_static', '(ratio)'] = c_p_static
    df_experiment['c_p_total', '(ratio)'] = c_p_total
    df_experiment['closest_match', '(ratio)'] = closest_match


def enhance_pitch_and_yaw(df_experiment, df_interpolation):
    print("enhancing accuracy of pitch (alpha) and yaw (beta) of measured parameters")
    prev_resolution = df_experiment['resolution'].iat[1, 0]
    resolution_pitch = abs(df_interpolation['pitch'].iat[1, 0]-df_interpolation['pitch'].iat[2, 0])
    resolution_yaw = abs(df_interpolation['yaw'].iat[1, 0] - df_interpolation['yaw'].iat[2, 0])
    resolution = max(resolution_pitch, resolution_yaw)
    df_experiment['resolution', '(deg)'] = np.zeros((df_experiment.shape[0], 1), dtype=float) + resolution
    print(f"enhancement resolution is {resolution}")

    c_p_labels = list()
    for index, headings in enumerate(list(df_experiment.columns)):
        if 'c_p_local' in headings[0]:
            c_p_labels.append(headings[0])
    n_measurements = df_experiment.shape[0]
    c_p_experiment = np.array(df_experiment[c_p_labels]).astype(float)
    c_p_interpolation = np.array(df_interpolation[c_p_labels]).astype(float)
    c_p_total, c_p_static = np.array(list()), np.array(list())
    yaw, pitch = np.array(list()), np.array(list())
    closest_match = np.array(list())

    yaw_all = np.array(df_interpolation['yaw']).flatten()
    pitch_all = np.array(df_interpolation['pitch']).flatten()
    yaw_min = np.array(df_experiment['yaw']).flatten() - prev_resolution
    pitch_min = np.array(df_experiment['pitch']).flatten() - prev_resolution
    yaw_max = np.array(df_experiment['yaw']).flatten() + prev_resolution
    pitch_max = np.array(df_experiment['pitch']).flatten() + prev_resolution

    interpolation_c_p_static = np.array(df_interpolation['c_p_static'])
    interpolation_c_p_total = np.array(df_interpolation['c_p_total'])
    interpolation_pitch = np.array(df_interpolation['pitch'])
    interpolation_yaw = np.array(df_interpolation['yaw'])

    for row_index, c_p_point in enumerate(c_p_experiment, start=0):
        valid_indices = np.where((yaw_all > yaw_min[row_index]) & (yaw_all < yaw_max[row_index]) &
                                 (pitch_all > pitch_min[row_index]) & (pitch_all < pitch_max[row_index]))[0]
        c_p_interpolation_valid = (c_p_interpolation[valid_indices])
        match_array = np.sum((c_p_point - c_p_interpolation_valid) ** 2, axis=1)
        closest_match_idx = np.argmin(match_array)
        closest_match_val = match_array[closest_match_idx]
        valid_idx = valid_indices[closest_match_idx]
        c_p_static = np.append(c_p_static, interpolation_c_p_static[valid_idx])
        c_p_total = np.append(c_p_total, interpolation_c_p_total[valid_idx])
        pitch = np.append(pitch, interpolation_pitch[valid_idx])
        yaw = np.append(yaw, interpolation_yaw[valid_idx])
        closest_match = np.append(closest_match, closest_match_val)
        print(f"enhancing point {row_index + 1} of {n_measurements}")

    df_experiment['pitch', '(deg)'] = pitch
    df_experiment['yaw', '(deg)'] = yaw
    df_experiment['c_p_static', '(ratio)'] = c_p_static
    df_experiment['c_p_total', '(ratio)'] = c_p_total
    df_experiment['closest_match', '(ratio)'] = closest_match


def calculate_velocity_components(df_experiment, switch_y_and_z=False):
    print("calculating flow velocity components")
    pitch_rad = np.deg2rad(np.array(df_experiment['pitch']))
    yaw_rad = np.deg2rad(np.array(df_experiment['yaw']))
    pressure_range = (np.array(df_experiment['pressure_range']))
    density = (np.array(df_experiment['density']))
    c_p_static = (np.array(df_experiment['c_p_static']))
    c_p_total = (np.array(df_experiment['c_p_total']))
    velocity_mag = np.sqrt((2 * pressure_range / density) * (c_p_static - c_p_total + 1))
    velocity_x = velocity_mag * np.cos(pitch_rad) * np.cos(yaw_rad)
    velocity_y = velocity_mag * np.sin(pitch_rad)
    velocity_z = velocity_mag * np.cos(pitch_rad) * np.sin(yaw_rad)
    df_experiment['velocity_mag', '(m/s)'] = velocity_mag
    df_experiment['velocity_x', '(m/s)'] = velocity_x
    if switch_y_and_z is False:
        df_experiment['velocity_y', '(m/s)'] = velocity_y
        df_experiment['velocity_z', '(m/s)'] = velocity_z
    else:
        print('switching y and z velocity components ')
        df_experiment['velocity_y', '(m/s)'] = velocity_z
        df_experiment['velocity_z', '(m/s)'] = velocity_y


def calculate_pitot_rake_velocities(df_experiment, channels):
    print("calculating flow velocity from Pitot Rake pressures")
    densities = np.array(df_experiment['density'])
    pressure_names, velocity_names = list(), list()
    for index, channel in enumerate(channels):
        pressure_labels = f'P{channel}'
        velocity_labels = f'V{index}'
        pressure_names.append(pressure_labels)
        velocity_names.append(velocity_labels)
        pressures = np.array(df_experiment[pressure_labels])
        velocities = pressures / (0.5 * densities)
        velocities[velocities < 0] = 0
        velocities = np.sqrt(velocities)
        df_experiment[velocity_labels, '(m/s)'] = velocities
        temporary_list = list()
        for count, old_column in enumerate(pressure_labels, start=1):
            new_column = f'temporary{count}'
            temporary_list.append(new_column)
            df_experiment.rename(columns={old_column: new_column}, inplace=True)
        for count, old_column in enumerate(temporary_list, start=1):
            new_column = f'P{count}'
            df_experiment.rename(columns={old_column: new_column}, inplace=True)
    return pressure_names, velocity_names


def create_variable_to_unit_dictionary(data_frame):
    var_to_unit = {}
    for index, header in enumerate(list(data_frame.columns)):
        var_to_unit[header[0]] = header[1]
    var_to_unit['turb_int'] = '(ratio)'
    return var_to_unit


def check_probe_and_printer_overlap(df_measurements, df_printer):
    printer_start, printer_end = df_printer['epoch_start'].iat[0, 0], df_printer['epoch_end'].iat[0, 0]
    probe_start, probe_end = df_measurements['epoch'].iat[0, 0], df_measurements['epoch'].iat[-1, 0]
    if printer_start < probe_start and printer_end > probe_end:
        print("WARNING: sampling was turned on too late and turned off too early")
        exit()
    elif printer_start < probe_start:
        overlap = round((probe_start - printer_start), 2)
        print(f"WARNING: sampling was turned on too late by {overlap} seconds")
        if overlap > 4:
            print("terminating early")
            exit()
    elif printer_end > probe_end:
        overlap = round((printer_end - probe_end), 2)
        print(f"WARNING: sampling was turned off too early by {overlap} seconds")
        exit()
    else:
        print("sampling times and position times overlap correctly")


def find_start_and_end_indices(df_measurements, df_printer):
    printer_starts, printer_ends = np.array(df_printer['epoch_start']), np.array(df_printer['epoch_end'])
    probe_epochs = np.array(df_measurements['epoch'])
    points = df_printer.shape[0]
    index_starts, index_ends = np.zeros(points).astype(int), np.zeros(points).astype(int)
    start, counter = True, 0
    for index, probe_epoch in enumerate(probe_epochs):
        if printer_starts[counter] <= probe_epoch <= printer_ends[counter]:
            if start is True:
                index_starts[counter] = index
                start = False
        else:
            if start is False:
                index_ends[counter] = index - 1
                counter += 1
                start = True
        if counter == points:
            break
    return index_starts, index_ends


def calculate_avg_std_cov(df_processed, df_measurements, process, unit, index_starts, index_ends):
    data = np.array(df_measurements[process])
    averages = np.array(list())
    standard_deviations = np.array(list())
    coefficients_of_variation = np.array(list())
    for index_start, index_end in zip(index_starts, index_ends):
        average = np.average(data[index_start:index_end])
        averages = np.append(averages, average)
        standard_deviation = np.std(data[index_start:index_end])
        standard_deviations = np.append(standard_deviations, standard_deviation)
        if average != 0:
            coefficients_of_variation = np.append(coefficients_of_variation, standard_deviation / average)
        else:
            coefficients_of_variation = np.append(coefficients_of_variation, 0)
    df_processed[f'{process}_avg', unit] = averages
    df_processed[f'{process}_std', unit] = standard_deviations
    df_processed[f'{process}_cov', unit] = coefficients_of_variation


def filter_multi_hole_probe_field(df_measurements, df_printer):
    check_probe_and_printer_overlap(df_measurements, df_printer)
    print("filtering measured multi-hole probe data based on coordinates")
    index_starts, index_ends = find_start_and_end_indices(df_measurements, df_printer)

    df_processed = pd.DataFrame()
    df_processed['probe_x'] = df_printer['probe_x']
    df_processed.columns = pd.MultiIndex.from_product([df_processed.columns, ['(mm)']])
    df_processed['probe_y', 'mm'] = df_printer['probe_y']

    variables = ['yaw', 'pitch', 'density', 'temperature', 'velocity_mag',
                 'velocity_x', 'velocity_y', 'velocity_z', 'closest_match']
    variable_units = ['(deg)', '(deg)', '(kg/m^3)', '(deg C)', '(m/s)', '(m/s)', '(m/s)', '(m/s)', '(ratio)']
    for variable, unit in zip(variables, variable_units):
        calculate_avg_std_cov(df_processed, df_measurements, variable, unit, index_starts, index_ends)

    velocity_mag = np.array(df_measurements['velocity_mag'])
    turbulence_intensity = np.array(list())
    for index_start, index_end in zip(index_starts, index_ends):
        point_velocities = velocity_mag[index_start:index_end]
        average_velocity = np.average(point_velocities)
        samples = len(point_velocities)
        deviation = np.sum((point_velocities - average_velocity) ** 2)
        turbulence_intensity = np.append(turbulence_intensity, ((1 / samples) * deviation) ** 0.5 / average_velocity)
    df_processed[f'turb_int', '(ratio)'] = turbulence_intensity
    return df_processed


def filter_pitot_rake_field(df_measurements, df_printer, pitot_rake_offsets, offset_in_x):
    check_probe_and_printer_overlap(df_measurements, df_printer)
    print("filtering measured pitot rake data based on coordinates")
    index_starts, index_ends = find_start_and_end_indices(df_measurements, df_printer)

    probe_x_in = np.array(df_printer['probe_x']).flatten()
    probe_y_in = np.array(df_printer['probe_y']).flatten()
    df_split = pd.DataFrame()
    df_split['probe_x'] = probe_x_in
    df_split.columns = pd.MultiIndex.from_product([df_split.columns, ['(mm)']])
    df_split['probe_y', 'mm'] = probe_y_in
    variables, variable_units = ['P', 'V'], ['(Pa)', '(m/s)']
    for var, unit in zip(variables, variable_units):
        for idx, offset in enumerate(pitot_rake_offsets):
            calculate_avg_std_cov(df_split, df_measurements, f'{var}{idx}', unit, index_starts, index_ends)

    probe_x = np.array(list())
    probe_y = np.array(list())
    for offset in pitot_rake_offsets:
        if offset_in_x:
            probe_y = np.append(probe_y, probe_y_in)
            probe_x = np.append(probe_x, probe_x_in + offset)
        else:
            probe_x = np.append(probe_x, probe_x_in)
            probe_y = np.append(probe_y, probe_y_in + offset)

    df_processed = pd.DataFrame()
    df_processed['probe_x'] = probe_x
    df_processed.columns = pd.MultiIndex.from_product([df_processed.columns, ['(mm)']])
    df_processed['probe_y', '(mm)'] = probe_y
    endings = ['avg', 'std', 'cov']
    for end in endings:
        for var, var_units in zip(variables, variable_units):
            array = np.array(list())
            for idx, offset in enumerate(pitot_rake_offsets):
                array = np.append(array, np.array(df_split[f'{var}{idx}_{end}']))
            if end == 'cov':
                var_units = '(ratio)'
            df_processed[f'{var}_{end}', var_units] = array
    if offset_in_x:
        df_processed = df_processed.sort_values(by=[('probe_x', '(mm)'), ('probe_y', '(mm)')])
    else:
        df_processed = df_processed.sort_values(by=[('probe_y', '(mm)'), ('probe_x', '(mm)')])
    return df_processed


def filter_data_into_time_frames(df_measurements, time_frames, names, reduction, units, variables):
    var_to_unit = create_variable_to_unit_dictionary(df_measurements)
    if reduction is None or reduction < 1:
        print('reduction is forced to be 1')
        reduction = 1
    if len(time_frames) != len(names):
        print('ERROR: Number of timeframes must match timeframe names')
    starts = np.array(time_frames)[:, 0]
    ends = starts + np.array(time_frames)[:, 1]
    probe_times = np.array(df_measurements['time'])
    sample_duration = float((probe_times[1] - probe_times[0]))
    max_sample_number = int(np.amax(ends - starts) / sample_duration)
    frame_duration = float(sample_duration * max_sample_number)
    df_std = pd.DataFrame()
    df_std['time'] = np.linspace(sample_duration, frame_duration, max_sample_number)
    df_std.columns = pd.MultiIndex.from_product([df_std.columns, ['(s)']])    # initialise multi-index
    df_smooth = df_std.copy()

    for name, start, end in zip(names, starts, ends):
        min_index = np.where(probe_times == start)[0][0]
        max_index = np.where(probe_times == end)[0][0]
        for variable in variables:
            array = np.array(df_measurements[variable])[min_index:max_index]
            temp_length = len(array)
            if temp_length < max_sample_number:
                nan_array = np.empty(max_sample_number - temp_length)
                nan_array[:] = np.nan
                array = np.append(array, nan_array)
            new_name = f'{variable}@{name}_{units[1]}'
            df_std[new_name, var_to_unit[variable]] = array
            df_smooth[new_name, var_to_unit[variable]] = df_std[new_name].rolling(int(reduction)).mean()
    return df_std, df_smooth


def calculate_time_frame_averages(df_measurements, df_std, variables, names, unit):
    var_to_unit = create_variable_to_unit_dictionary(df_measurements)
    df_avg = pd.DataFrame()
    df_avg[unit[0]] = names
    df_avg.columns = pd.MultiIndex.from_product([df_avg.columns, [unit[1]]])  # initialise multi-index
    for variable in variables:
        averages = list()
        for name in names:
            new_name = f'{variable}@{name}_{unit[1]}'
            average = np.average(np.array(df_std[new_name]))
            averages.append(average)
        df_avg[variable, var_to_unit[variable]] = averages
    return df_avg


def find_corner_and_edge_indices(df_printer, ignore_edges, ignore_corners_1, ignore_corners_3):
    if ignore_edges is False and ignore_corners_3 is False and ignore_corners_1 is False:
        return
    probe_x = np.array(df_printer['probe_x'])
    probe_y = np.array(df_printer['probe_y'])
    if ignore_edges is True or ignore_corners_3 is True or ignore_corners_1 is True:
        min_x_indices = np.argwhere(probe_x == min(probe_x)).flatten().flatten().tolist()
        max_x_indices = np.argwhere(probe_x == max(probe_x)).flatten().flatten().tolist()
        min_y_indices = np.argwhere(probe_y == min(probe_y)).flatten().flatten().tolist()
        max_y_indices = np.argwhere(probe_y == max(probe_y)).flatten().flatten().tolist()

        second_min_x_indices = np.argwhere(probe_x == np.unique(probe_x)[1].flatten().flatten().tolist())
        second_max_x_indices = np.argwhere(probe_x == np.unique(probe_x)[-2].flatten().flatten().tolist())
        second_min_y_indices = np.argwhere(probe_y == np.unique(probe_y)[1].flatten().flatten().tolist())
        second_max_y_indices = np.argwhere(probe_y == np.unique(probe_y)[-2].flatten().flatten().tolist())

        min_max_x_indices = np.unique(np.concatenate((min_x_indices, max_x_indices), 0))
        min_max_y_indices = np.unique(np.concatenate((min_y_indices, max_y_indices), 0))
        second_min_max_x_indices = np.unique(np.concatenate((second_min_x_indices, second_max_x_indices), 0))
        second_min_max_y_indices = np.unique(np.concatenate((second_min_y_indices, second_max_y_indices), 0))

        edge_indices = np.unique(np.concatenate((min_max_x_indices, min_max_y_indices), 0))
        corner_indices_1 = np.intersect1d(min_max_x_indices, min_max_y_indices)
        corner_indices_3_x = np.intersect1d(second_min_max_x_indices, min_max_y_indices)
        corner_indices_3_y = np.intersect1d(second_min_max_y_indices, min_max_x_indices)
        corner_indices_3 = np.unique(np.concatenate((corner_indices_1, corner_indices_3_x, corner_indices_3_y)))

    if ignore_edges is True:
        ignore_indices = edge_indices
        print(f"all edge points are not considered (list below):")
        print(f'-> {ignore_indices}')
    elif ignore_corners_3 is True:
        ignore_indices = corner_indices_3
        print(f"three points in each corner are not considered (list below):")
        print(f'-> {ignore_indices}')
    elif ignore_corners_1 is True:
        ignore_indices = corner_indices_1
        print(f"one point in each corner are not considered (list below):")
        print(f'-> {ignore_indices}')
    else:
        ignore_indices = list()
    return ignore_indices


def remove_indices_from_measurements(data_frame, ignore_indices):
    df_copy = data_frame.copy()
    if len(ignore_indices) != 0:
        df_copy.drop(df_copy.index[ignore_indices])
    return df_copy


def calculate_average_field_values(data_frame):
    headings = list()
    units = list()
    for heading_pair in list(data_frame.columns):
        heading, unit = tuple(heading_pair)
        if 'avg' in heading or 'turb_int' in heading:
            headings.append(heading)
            units.append(unit)
    df_fields = pd.DataFrame()
    first = True
    for heading, unit in zip(headings, units):
        average = np.average(np.array(data_frame[heading]))
        standard_deviation = np.std(np.array(data_frame[heading]))
        heading = heading.replace('_avg', '')
        if first is True:
            first = False
            df_fields[f'{heading}_avg'] = [average]
            df_fields.columns = pd.MultiIndex.from_product([df_fields.columns, [unit]])
        else:
            df_fields[f'{heading}_avg', unit] = [average]
        df_fields[f'{heading}_std', unit] = [standard_deviation]
        df_fields[f'{heading}_cov', '(ratio)'] = [standard_deviation / average]
    return df_fields


# end of code
