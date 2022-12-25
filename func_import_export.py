"""This Python module contains a set of functions related to importing and exporting of experimental data gathered
by a variety of pressure measuring devices"""

import os
import pandas as pd
from func_data import *


# -------------------- functions for importing data  -------------------- #

def import_csv_pandas(file_location):  # import pressure raw calibration data using pandas
    print(f"importing {file_location}")
    content = pd.read_csv(file_location, header=[0, 1])
    return content


def import_surrey_pandas(file_location):  # import surrey sensor data using pandas
    print(f"importing {file_location}")
    content = pd.read_csv(file_location, sep='\t', lineterminator='\r', skiprows=[1, -1])
    return content


def combine_pressure_and_density(pressure_location, density_location, channels, channel_names=None):

    print("combining pressure and density data")
    df_pressure = import_surrey_pandas(pressure_location)
    df_density = import_surrey_pandas(density_location)
    start_time = df_pressure['Record start time'][1].strip('\n')
    start_epoch = timestamp_to_epoch(start_time, '%d/%m/%Y %H:%M:%S')
    sample_ratio = df_density['t (s)'][1] / df_pressure['t (s)'][1]
    trim = int(len(df_pressure['t (s)']) - len(df_density['t (s)']) * sample_ratio)

    trim_p, trim_d = -1, -1
    if trim > 0:
        trim_p, trim_d = -1 - trim, -1
    elif trim < 0:
        trim_p, trim_d = -1, -1 + trim

    df_combined = pd.DataFrame()
    df_combined['time'] = df_pressure['t (s)'][0:trim_p]
    df_combined.columns = pd.MultiIndex.from_product([df_combined.columns, ['(s)']])    # initialise multi-index
    df_combined['time', '(s)'] = df_pressure['t (s)'][0:trim_p]
    df_combined['epoch', '(s)'] = df_pressure['t (s)'][0:trim_p] + start_epoch
    df_combined.epoch = df_pressure['t (s)'][0:trim_p] + start_epoch

    print("creating correct timestamps")
    """
    timestamps = np.array(list())
    for epoch in df_combined['epoch', '(s)']:
        timestamps = np.append(timestamps, epoch_to_timestamp(epoch))
    """
    timestamps = [f"{start_time}" for x in range(len(df_combined['time']))]
    df_combined['timestamp', '(date time)'] = timestamps
    df_combined['density', '(kg/m^3)'] \
        = np.array(df_density['Density (kg/m^3)']).repeat(sample_ratio, axis=0)[0:trim_d]
    df_combined['temperature', '(deg C)'] \
        = np.array(df_density['Thermistor (degC)']).repeat(sample_ratio, axis=0)[0:trim_d]
    if channel_names is None:
        for channel in channels:
            df_combined[f'P{channel}', '(Pa)'] = df_pressure[f'P{channel} (Pa)'][0:trim_p]
    else:
        for channel_name, channel in zip(channel_names, channels):
            df_combined[f'{channel_name}', '(Pa)'] = df_pressure[f'P{channel} (Pa)'][0:trim_p]
    return df_combined


# -------------------- functions for exporting data  -------------------- #


def create_new_directory(directory):
    path = directory
    try:
        os.mkdir(path)
    except OSError:
        print("A new directory named %s could not be created" % path)
    else:
        print("Successfully created the new directory %s " % path)


def export_data_csv(data_frame, file_name):
    row_0, row_1 = str(), str()
    for index, header in enumerate(list(data_frame.columns)):
        row_0 = row_0 + str(header[0]) + ','
        row_1 = row_1 + str(header[1]) + ','
    row_0 = row_0.rstrip(row_0[-1]) + "\n"
    row_1 = row_1.rstrip(row_1[-1]) + "\n"
    with open(file_name, 'w', encoding='utf-8-sig') as file:
        file.write(row_0)
        file.write(row_1)
    data_frame.to_csv(file_name, index=False, header=False, encoding='utf-8', mode='a')
    print(f"successfully exported data to {file_name}")


def log_printer_to_csv(df_combined, printer_log_location):
    with open(printer_log_location, 'r') as file:           # search file for sampling date
        for line in file:
            if line.count("-") >= 3:
                print("analysing printer locations using new format")
                buffer = [1.5, 1.5]
                df_printer = log_printer_to_csv_new(buffer, printer_log_location)
            else:
                print("analysing printer locations using old format")
                buffer = [2, 2]
                date = df_combined['timestamp', '(date time)'][0].split(" ")[0]
                df_printer = log_printer_to_csv_old(buffer, printer_log_location, date)
            break
    return df_printer


def log_printer_to_csv_new(buffer, printer_log_location):
    date_format = '%Y-%m-%d %H:%M:%S.%f'
    with open(printer_log_location, 'r') as file:           # search file for sampling time
        for line in file:
            if line.find("sampling time") > -1:
                text = str(line).replace('\"', '').split()
                sampling_time = float(text[-1])
                break

    buffer_start, buffer_end = buffer[0], buffer[1]
    with open(printer_log_location, 'r') as file:
        for line in file:
            if line.find("X = ") > -1:
                text = str(line).replace('\"', '').replace(', ', ' ').replace(',', '.').split()
                start_epoch = timestamp_to_epoch(f"{text[0]} {text[1]}", date_format)
                break

    with open(printer_log_location, 'r') as file:           # search file for data coordinates and times
        printer_x, printer_z = np.array(list()), np.array(list())
        epoch_starts, epoch_ends, durations = np.array(list()), np.array(list()), np.array(list())
        for line in file:
            if line.find("X = ") > -1:                      # search for x and z coordinates
                text = str(line).replace('\"', '').replace(', ', ' ').replace(',', '.').split()
                printer_x = np.append(printer_x, text[-4])
                printer_z = np.append(printer_z, text[-1])
                epoch = timestamp_to_epoch(f"{text[0]} {text[1]}", date_format)
                epoch_start = epoch + buffer_start
                epoch_end = epoch + sampling_time - buffer_end
                duration = sampling_time
                epoch_starts = np.append(epoch_starts, epoch_start)
                epoch_ends = np.append(epoch_ends, epoch_end)
                durations = np.append(durations, duration)
    starts, ends = epoch_starts - start_epoch, epoch_ends - start_epoch

    df_printer = pd.DataFrame()
    df_printer['start', '(s)'] = starts
    df_printer['end', '(s)'] = ends
    df_printer['duration', '(s)'] = durations
    df_printer['epoch_start', '(s)'] = epoch_starts
    df_printer['epoch_end', '(s)'] = epoch_ends
    df_printer['probe_x', '(mm)'] = printer_x
    df_printer['probe_y', '(mm)'] = printer_z
    return df_printer


def log_printer_to_csv_old(buffer, printer_log_location, date):

    found_sampling_time, found_start_time = False, False
    with open(printer_log_location, 'r') as file:           # search file for sampling time
        for line in file:
            if found_sampling_time is True and found_start_time is True:
                break
            if found_sampling_time is False and line.find("sampling time") > -1:
                text = str(line).replace('\"', '').split()
                sampling_time = float(text[-1])
                found_sampling_time = True
            if found_start_time is False and line.find("Print started at:") > -1:
                text = str(line).replace('\"', '').split()
                start_time = text[-1]
                found_start_time = True

    buffer_start, buffer_end = buffer[0], buffer[1]
    with open(printer_log_location, 'r') as file:           # search file for data coordinates and times
        printer_x, printer_z = np.array(list()), np.array(list())
        starts, ends, durations = np.array(list()), np.array(list()), np.array(list())
        for line in file:
            if line.find("X = ") > -1:  # search for x and z coordinates
                text = str(line).replace('\"', '').replace(',', '').split()
                printer_x = np.append(printer_x, text[-4])
                printer_z = np.append(printer_z, text[-1])
            if line.find("Print time:") > -1:  # search for printer time stamps
                text = str(line).replace('m', '').replace('s', '').split()
                try:
                    minutes = float(text[-2])
                except:
                    minutes = float(0)
                seconds = float(text[-1])
                start = minutes * 60 + seconds + buffer_start
                end = minutes * 60 + seconds + sampling_time - buffer_end
                duration = end - start
                starts = np.append(starts, start)
                ends = np.append(ends, end)
                durations = np.append(durations, duration)
    epoch = timestamp_to_epoch(str(date + " " + start_time), '%d/%m/%Y %H:%M:%S')
    epoch_starts, epoch_ends = starts + epoch, ends + epoch

    df_printer = pd.DataFrame()
    df_printer['start', '(s)'] = starts
    df_printer['end', '(s)'] = ends
    df_printer['duration', '(s)'] = durations
    df_printer['epoch_start', '(s)'] = epoch_starts
    df_printer['epoch_end', '(s)'] = epoch_ends
    df_printer['probe_x', '(mm)'] = printer_x
    df_printer['probe_y', '(mm)'] = printer_z
    return df_printer
# end of code
