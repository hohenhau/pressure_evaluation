"""This Python control module specifies all required input parameters for the run scripts"""


# Parameters to *INTERPOLATE* the initial calibration (run_interpolate)
original_size = 3.0     # specify the calibration cell size in degrees
interp_size = 1.0       # specify the interpolation cell size in degrees


# Parameters to *MODIFY PRINTER COORDINATES*
flip_x = True          # flip coordinates horizontally
flip_y = False          # flip coordinates vertically
no_edges = False        # ignore the outer measurements in calculating the averages
no_corners_1 = False    # ignore single point located in each corner
no_corners_3 = False    # ignore the three points located in each corner

# Parameters to *CONVERT MULTI-HOLE PRESSURES TO VELOCITIES* (run_multi_hole_velocity)
switch_y_and_z = True
multi_hole_pressure_channels = [0, 1, 2, 3, 4, 5, 6]

# Parameters to *ASSIGN MULTI-HOLE VELOCITIES TO COORDINATES* based on location (run_multi_hole_field)
multi_hole_export_field = ['probe_x', 'probe_y', 'yaw_avg', 'pitch_avg', 'velocity_mag_avg', 'velocity_x_avg',
                           'velocity_x_std', 'velocity_y_avg', 'velocity_z_avg', 'turb_int']
multi_hole_export_average = ['yaw_avg', 'pitch_avg', 'velocity_mag_avg', 'velocity_x_avg', 'velocity_x_std',
                             'velocity_y_avg', 'velocity_z_avg', 'turb_int_avg']
multi_hole_export_graph = ['velocity_mag_avg', 'velocity_x_avg', 'velocity_y_avg', 'velocity_z_avg', 'turb_int']
multi_hole_normalise = False
multi_hole_norm_factor = 32
multi_hole_norm_limits = [None, None]
multi_hole_export_limits = [[None, None], [None, None], [None, None], [None, None], [None, None]]
mh_glyph, mh_scat, mh_heat, mh_cont = True, True, True, True

# Parameters to *ASSIGN MULTI-HOLE VELOCITIES TO TIMEFRAMES* at a single measured point (run_multi_hole_time_frames)
duration_probe = d = 20  # Time frame format = (start time (s), duration (s))
time_frames_probe = [(15, d), (45, d), (75, d), (105, d), (135, d), (165, d), (195, d), (225, d), (255, d), (285, d)]
time_frame_names_probe = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]      # specify the input time frame names
moving_average_span_probe = 5                                           # specify optional down-sampling factor
labels_probe = ['Rotational Speed', '(RPM)']                            # label and units for graphing y-axis
variables_probe = ['velocity_x']                                        # variables to be analysed


# Parameters to *CONVERT PITOT RAKE PRESSURES TO VELOCITIES* (run_pitot_rake_velocity)
pitot_rake_channels = [0, 1, 2, 3, 4, 5, 6, 7]

# Parameters to *ASSIGN PITOT RAKE VELOCITIES TO COORDINATES* (run_pitot_rake_field)
pitot_rake_offsets = [0.000, 3.125, 6.250, 9.375, 12.500, 15.625, 18.750, 21.875]
offset_in_x = True
pitot_rake_export_field = ['probe_x', 'probe_y', 'V_avg', 'P_avg', 'V_std', 'P_std', 'V_cov', 'P_cov']
pitot_rake_export_average = ['V_avg', 'P_avg', 'V_std', 'P_std', 'V_cov', 'P_cov']
pitot_rake_export_graph = ['V_avg', 'V_std', 'V_cov']
pitot_normalise = True
pitot_norm_factor = 18.36
pitot_norm_limits = [None, None]
pitot_rake_export_limits = [[None, None], [None, None], [None, None], [None, None], [None, None]]
pr_scat, pr_heat, pr_cont = True, True, True


# Parameters to *ASSIGN PRESSURE TAP READINGS* to specific time frames and locations (run_pressure_tap_time_frames)
duration_tap = t = 20  # Time frame format = (start time (s), duration (s))
time_frames_tap = [(15, t), (45, t), (75, t), (105, t), (135, t), (165, t), (195, t), (225, t), (255, t), (285, t)]
time_frame_names_tap = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]        # specify the input time frame names
moving_average_span_tap = 5                                             # specify optional down-sampling factor
labels_tap = ['Rotational Speed', '(RPM)']                              # label and units for graphing y-axis
sensor_list = [None for x in range(64)]                                 # pressure channel location/name
sensor_list[8] = 'REF straight 3 downstream to scanner'
sensor_list[16] = 'vanes downstream close'
sensor_list[17] = 'vanes downstream far'
sensor_list[18] = 'straight 1 upstream'
sensor_list[19] = 'straight 1 downstream'
sensor_list[20] = 'straight 2 downstream'
sensor_list[21] = 'straight 3 upstream'
sensor_list[22] = 'straight 4 upstream'
sensor_list[23] = 'straight 4 downstream'

# end of code
