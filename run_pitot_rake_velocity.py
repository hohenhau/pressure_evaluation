#!/usr/bin/env python3
"""This Python script takes the raw measurement log files relating to a multi-hole probe, and estimates the
experimental velocity components. Printer log locations are also reformatted for ease of access"""

import os
from func_import_export import *
import var_locations
import var_variables

pressure_input_log = var_locations.pressure_input_log
density_input_log = var_locations.density_input_log
printer_input_log = var_locations.printer_input_log
printer_output = var_locations.printer_output
pitot_rake_output = var_locations.pitot_rake_output

pitot_rake_channels = var_variables.pitot_rake_channels
df_experiment = combine_pressure_and_density(pressure_input_log, density_input_log, pitot_rake_channels)
pressure_names, velocity_names = calculate_pitot_rake_velocities(df_experiment, pitot_rake_channels)
exports_additional = ['timestamp', 'epoch', 'time', 'density', 'temperature']
df_export = df_experiment[exports_additional + pressure_names + velocity_names].copy()
export_data_csv(df_export, pitot_rake_output)
if os.path.exists(printer_input_log):
    df_printer = log_printer_to_csv(df_experiment, printer_input_log)
    export_data_csv(df_printer, printer_output)
else:
    print('No input printer coordinate log was found')

# end of code
