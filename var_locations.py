"""This Python control module specifies all required file locations and names for the run scripts"""


# The general directories
time_directory = str("20220212_2327")
calibration_directory = str('data_calibrated')
measured_directory = str("data_measured")
processed_directory = str("data_processed")
experimental_directory = str(f'{processed_directory}/{time_directory}')
pressure_input_log = str(f'{measured_directory}/{time_directory}/log_pressure.txt')
density_input_log = str(f'{measured_directory}/{time_directory}/log_additional.txt')
printer_input_log = str(f'{measured_directory}/{time_directory}/log_printer.txt')
printer_output = str(f'{measured_directory}/{time_directory}/measured_printer_{time_directory}.csv')


# File locations to *INTERPOLATE* the initial calibration (run_interpolate)
calibration_input_file = str(f'{calibration_directory}/calibration_60x60_3deg.csv')  # specify name of input file
calibration_figure_directory = str('figures_calibrated/')
interpolation_data_directory = str('data_interpolated/')
interpolation_figure_directory = str('figures_interpolated/')


# File locations to *CONVERT MULTI-HOLE PRESSURES TO VELOCITIES* (run_multi_hole_velocity)
multi_hole_output = str(f'{measured_directory}/{time_directory}/measured_multi_hole_probe_{time_directory}.csv')
interpolation_file_coarse = str('data_interpolated/interpolation_1-00.csv')
interpolation_file_fine = str('data_interpolated/interpolation_0-20.csv')

# File locations *ASSIGNING MULTI-HOLE VELOCITIES TO COORDINATES* based on probe location (run_multi_hole_field)
multi_hole_input_printer = printer_output
multi_hole_input_field = multi_hole_output
multi_hole_points = str(f'{processed_directory}/{time_directory}/multi_hole_field_points_{time_directory}.csv')
multi_hole_field = str(f'{processed_directory}/{time_directory}/multi_hole_field_average_{time_directory}.csv')


# File locations *ASSIGNING MULTI-HOLE VELOCITIES TO TIMEFRAMES* at single measured point (run_multi_hole_time_frames)
multi_hole_input_points = multi_hole_output
multi_hole_frames = str(f'{processed_directory}/{time_directory}/multi_hole_point_time_{time_directory}.csv')
multi_hole_smoothed = str(f'{processed_directory}/{time_directory}/multi_hole_point_smooth_{time_directory}.csv')
multi_hole_averaged = str(f'{processed_directory}/{time_directory}/multi_hole_point_average_{time_directory}.csv')


# File locations to *CONVERT PITOT RAKE PRESSURES TO VELOCITIES* (run_pitot_rake_velocity)
pitot_rake_output = str(f'{measured_directory}/{time_directory}/measured_pitot_rake_{time_directory}.csv')

# File locations *ASSIGNING PITOT RAKE VELOCITIES TO COORDINATES* based on probe location (run_pitot_rake_field)
pitot_rake_input_printer = printer_output
pitot_rake_input_field = pitot_rake_output
pitot_rake_points = str(f'{processed_directory}/{time_directory}/pitot_rake_field_points_{time_directory}.csv')
pitot_rake_field = str(f'{processed_directory}/{time_directory}/pitot_rake_field_average_{time_directory}.csv')


# File locations to *ASSIGN PRESSURE TAP READINGS* to specific time frames and locations (run_pressure_tap_time_frames)
tap_pressures_raw = str(f'{processed_directory}/{time_directory}/tap_pressure_raw_{time_directory}.csv')
tap_pressures_smoothed = str(f'{processed_directory}/{time_directory}/tap_pressure_smooth_{time_directory}.csv')
tap_pressures_averaged = str(f'{processed_directory}/{time_directory}/tap_pressure_avg_{time_directory}.csv')

# end of code
