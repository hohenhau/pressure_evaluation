"""This Python module contains a set of functions related to graphing data measured by a range of pressure
sensing devices"""

import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
from mpl_toolkits.axes_grid1 import make_axes_locatable


def check_data_format(df_grap):
    unique_x, unique_y = df_grap.unique_x, df_grap.unique_y
    if len(unique_x) > 1 and len(unique_y) > 1:     # check if data is in grid or line format
        grid_format = True
        print("Data is in grid format and can be plotted")
    else:
        grid_format = False
        print("Data is not in grid format and additional graphs will not be generated")
    if len(unique_x) <= 2:      # Check grid regularity for plotting
        x_regular = True
    else:
        x_regular = bool(round(unique_x[0] - unique_x[1], 1) == round(unique_x[1] - unique_x[2], 1))
    if len(unique_y) <= 2:
        y_regular = True
    else:
        y_regular = bool(round(unique_y[0] - unique_y[1], 1) == round(unique_y[1] - unique_y[2], 1))
    if x_regular is True and y_regular is True:
        grid_regular = True
        print("data does not form a regular grid structure")
    else:
        grid_regular = False
        print("data forms a regular grid structure")
    return grid_format, grid_regular


def graph_labels(graph_bundle, array_name, hole):
    if 'c_p_total' in array_name:
        graph_bundle.bar_unit = str("(ratio)")
        graph_bundle.heading = str("Total Pressure Coefficient")
    elif 'c_p_static' in array_name:
        graph_bundle.bar_unit = str("(ratio)")
        graph_bundle.heading = str("Static Pressure Coefficient")
    elif 'c_p' in array_name:
        graph_bundle.bar_unit = str("(ratio)")
        graph_bundle.heading = str(f"Local Pressure Coefficient (CJ{hole})")
    elif 'density' in array_name:
        graph_bundle.bar_unit = str("(kg/m^3)")
        graph_bundle.heading = f"Density ρ {graph_bundle.bar_unit}"
    elif 'pressure' in array_name:
        graph_bundle.bar_unit = str("(Pa)")
        graph_bundle.heading = f"Pressure {graph_bundle.bar_unit}"
    elif 'velocity' in array_name:
        end = str(array_name.split('_')[-2]).capitalize()
        graph_bundle.bar_unit = str("(m/s)")
        graph_bundle.heading = f"Velocity {end} {graph_bundle.bar_unit}"
    elif 'turb_int' in array_name:
        graph_bundle.bar_unit = str("(ratio)")
        graph_bundle.heading = f"Turbulence Intensity {graph_bundle.bar_unit}"


def tick_generator(num_low, num_high):
    if num_low == 0:
        mag_low = 0
    else:
        mag_low = math.floor(math.log(math.fabs(num_low), 10))
    if num_high == 0:
        mag_high = 0
    else:
        mag_high = math.floor(math.log(math.fabs(num_high), 10))
    mag_max = max(mag_low, mag_high) - 1
    bound_low = (math.floor(num_low / 10 ** mag_max) * (10 ** mag_max))
    bound_high = (math.ceil(num_high / 10 ** mag_max) * (10 ** mag_max))
    bound_range = bound_high - bound_low
    mag_range = math.floor(math.log(math.fabs(bound_range), 10))
    range_int = bound_range / 10 ** (mag_range - 1)
    preferences = list([7, 5, "7a", "5a", 6, "6a", 8, "8a", 4, "4a", 3, "3a"])
    for preference in preferences:
        if isinstance(preference, int):
            if range_int % preference == 0:
                ticks = np.linspace(bound_low, bound_high, preference + 1)
                break
        else:
            stripped = int(preference.strip("a"))
            if (range_int + 1) % stripped == 0:
                ticks = np.linspace(bound_low, (bound_high + 10 ** mag_max), stripped + 1)
                break
            else:
                ticks = np.linspace(bound_low, bound_high, 6)
                ticks = np.around(ticks, decimals=2)
    return ticks


def normalise_data(df_graph):
    print('normalising contours')
    df_graph.data = df_graph.data / df_graph.norm_factor            # normalise data
    df_graph.data_x = df_graph.data_x / df_graph.norm_factor        # normalise data
    df_graph.data_y = df_graph.data_y / df_graph.norm_factor        # normalise data
    df_graph.data_z = df_graph.data_z / df_graph.norm_factor        # normalise data
    df_graph.limits[0] = df_graph.normalised_limits[0]              # change limits
    df_graph.limits[1] = df_graph.normalised_limits[1]              # change limits


def check_limits(df_graph):
    lim_low, lim_high, data = df_graph.limits[0], df_graph.limits[1], np.array(df_graph.data)
    min_data, max_data = np.amin(data), np.amax(data)
    if lim_low is None and lim_high is None:
        ticks = tick_generator(min_data, max_data)            # generate ticks for colour bar
    elif lim_low is None:
        print(f"upper limit is forced below {lim_high}")                # print message to console
        ticks = tick_generator(np.amin(data), lim_high)                 # generate ticks for colour bar
    elif lim_high is None:
        print(f"lower limit is forced above {lim_low}")                 # print message to console
        ticks = tick_generator(lim_low, np.amax(data))                  # generate ticks for colour bar
    else:
        print(f"limits are forced between {lim_low} and {lim_high}")    # print message to console
        ticks = tick_generator(lim_low, lim_high)                       # generate ticks for colour bar
    t_min, t_max = np.amin(ticks), np.amax(ticks)                       # determine min/max values for colour bar
    return t_min, t_max, ticks


def create_heat_map(df_graph, safe_location):
    t_min, t_max, ticks = check_limits(df_graph)                                            # check and set graph limits
    pivot_table = df_graph.data_pivot
    figure, axis = plt.subplots()                                                           # generate figure and axes
    heat_map = axis.imshow(pivot_table, cmap="jet", vmin=t_min, vmax=t_max)                 # set values for axes
    axis.set_title(df_graph.heading)                                                        # set graph heading
    axis.set_xlabel(df_graph.x_axis_label)                                                  # set x label
    axis.set_ylabel(df_graph.y_axis_label)                                                  # set y label
    axis.set_xticks(df_graph.x_label_idx, labels=df_graph.x_label_val)                      # set x label values
    axis.set_yticks(df_graph.y_label_idx, labels=df_graph.y_label_val)                      # set y label values
    plt.imshow(pivot_table, origin='lower', cmap="jet")                                     # set bottom origin & colour
    divider = make_axes_locatable(axis)                                                     # make axes callable by code
    cax = divider.append_axes('right', size='5%', pad=0.1)                                  # set spacing to the axes
    bar_label = df_graph.bar_label
    plt.colorbar(heat_map, cax=cax, label=bar_label, ticks=ticks, orientation="vertical")   # create the color bar
    plt.tight_layout(pad=0.5)                                                               # set a tight layout
    plt.savefig(safe_location, dpi=300, bbox_inches='tight')                                # safe the figure
    plt.close(figure)                                                                       # close the figure
    print(f"saving heat map to {safe_location}")                                            # print progress to console


def create_contour_plot(df_graph, safe_location):
    t_min, t_max, ticks = check_limits(df_graph)    # check and set graph limits
    figure, axis = plt.subplots()                   # generate figure and axes
    axis.set_title(df_graph.heading)                # set graph heading
    axis.set_xlabel(df_graph.x_axis_label)          # set x label
    axis.set_ylabel(df_graph.y_axis_label)          # set y label
    axis.set_aspect('equal')                        # equal axis aspect ratio
    unique_x, unique_y, data_pivot = df_graph.unique_x, df_graph.unique_y, df_graph.data_pivot
    contour = axis.contourf(unique_x, unique_y, data_pivot, cmap="jet", levels=400, vmin=t_min, vmax=t_max)
    contour_map = ScalarMappable(norm=contour.norm, cmap=contour.cmap)
    boundaries = np.linspace(t_min, t_max, 400)
    values = (boundaries[:-1] + boundaries[1:]) / 2
    divider = make_axes_locatable(axis)                                                     # make axes callable by code
    cax = divider.append_axes('right', size='5%', pad=0.1)                                  # set spacing to the axes
    bar_label = df_graph.bar_label
    plt.colorbar(contour_map, ticks=ticks, cax=cax, label=bar_label, boundaries=boundaries, values=values)  # colour bar
    plt.tight_layout(pad=0.5)                                                               # set a tight layout
    plt.savefig(safe_location, dpi=300, bbox_inches='tight')                                # safe the figure
    plt.close(figure)                                                                       # close the figure
    print(f"saving contour plot to {safe_location}")                                        # print progress to console


def create_scatter_plot(df_graph, safe_location):
    t_min, t_max, ticks = check_limits(df_graph)                                        # check and set graph limits
    figure, axis = plt.subplots()                                                       # generate figure and axes
    axis.set_title(df_graph.heading)                                                    # set graph heading
    axis.set_xlabel(df_graph.x_axis_label)                                              # set x label
    axis.set_ylabel(df_graph.y_axis_label)                                              # set y label
    axis.set_aspect('equal')                                                            # equal axis aspect ratio
    colour_map = plt.cm.get_cmap('jet')                                                 # set plot colour scheme
    x, y, z = df_graph.x_coordinates, df_graph.y_coordinates, df_graph.data             # retrieve the colour map
    scatter = plt.scatter(x, y, c=z, s=40, cmap=colour_map, vmin=t_min, vmax=t_max)     # define the scatter data
    divider = make_axes_locatable(axis)                                                 # make axes callable by code
    cax = divider.append_axes('right', size='5%', pad=0.1)                              # set spacing to the axes
    plt.colorbar(scatter, cax=cax, ticks=ticks, label=df_graph.bar_label)               # create the color bar
    plt.tight_layout(pad=0.5)                                                           # set a tight layout
    plt.savefig(safe_location, dpi=300, bbox_inches='tight')                            # safe the figure
    plt.close(figure)                                                                   # close the figure
    print(f"saving scatter plot to {safe_location}")                                    # print progress to console


def create_glyph_plot(df_graph, safe_location):
    x_coords, y_coords = df_graph.x_coordinates, df_graph.y_coordinates
    data_y, data_z = df_graph.data_y, df_graph.data_z
    t_min, t_max, ticks = check_limits(df_graph)            # check and set graph limits
    figure, axis = plt.subplots()                           # generate figure and axes
    axis.set_title(df_graph.heading)                        # set graph heading
    axis.set_xlabel(df_graph.x_axis_label)                  # set x label
    axis.set_ylabel(df_graph.y_axis_label)                  # set y label
    axis.set_aspect('equal')                                # equal axis aspect ratio

    background_contour = True
    if background_contour is True:
        unique_x, unique_y, data_pivot = df_graph.unique_x, df_graph.unique_y, df_graph.data_pivot
        contour = axis.contourf(unique_x, unique_y, data_pivot, cmap="jet", levels=400, vmin=t_min, vmax=t_max)
        contour_map = ScalarMappable(norm=contour.norm, cmap=contour.cmap)
        boundaries = np.linspace(t_min, t_max, 400)                         # set colour levels
        values = (boundaries[:-1] + boundaries[1:]) / 2                     # set value to average of boundary pairs
        divider = make_axes_locatable(axis)                                 # make axes callable by code
        vectors = plt.quiver(x_coords, y_coords, data_y, data_z)            # plot a field of arrows
        cax = divider.append_axes('right', size='5%', pad=0.1)              # set spacing to the axes
        bar_label = df_graph.bar_label
        bar = plt.colorbar(contour_map, ticks=ticks, cax=cax, label=bar_label, boundaries=boundaries, values=values)
    else:
        vectors = plt.quiver(x_coords, y_coords, data_y, data_z)            # plot a field of arrows

    plt.tight_layout(pad=0.5)                                               # set a tight layout
    plt.savefig(safe_location, dpi=300, bbox_inches='tight')                # safe the figure
    plt.close(figure)                                                       # close the figure
    print(f"saving glyph plot to {safe_location}")                          # print progress to console

# end of code

