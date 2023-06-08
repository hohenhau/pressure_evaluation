import numpy as np
import math as math


class PointGrid:
    def __init__(self, x_array, y_array, cell_size):
        x_array, y_array = np.array(x_array), np.array(y_array)
        x_min = float(min(x_array))
        x_max = float(max(x_array))
        y_mior = float(min(y_array))
        y_max = float(max(y_array))
        self.n_rows = int(math.ceil(y_max - y_min) / cell_size) + 1
        self.n_columns = int(math.ceil((x_max - x_min) / cell_size)) + 1
        self.n_points = self.n_rows * self.n_columns
        self.x_indices = [0, self.n_rows - 1]
        self.y_indices = [0, self.n_columns - 1]
        print(f"interpolation raster = {self.n_rows} rows by {self.n_columns} columns ({self.n_points} points)")
        x_max = x_min + (self.n_columns * cell_size) - cell_size    # new maximum x-coordinate in raster
        y_max = y_min + (self.n_rows * cell_size) - cell_size       # new maximum y-coordinate in raster
        self.x_coord = np.linspace(x_min, x_max, self.n_columns)    # generate x-coordinate of cell centres
        self.y_coord = np.linspace(y_min, y_max, self.n_rows)       # generate y-coordinate of cell centres
        tile = np.tile(self.x_coord, self.n_rows)
        repeat = np.repeat(self.y_coord, self.n_columns)
        self.xy_interpolated = np.column_stack((tile, repeat))  # xy array


class GraphBundle:  # Sort dimensionless parameter values into a pivot table for graphing
    def __init__(self, x_coordinates, y_coordinates):
        self.x_coordinates = np.array(x_coordinates)
        self.y_coordinates = np.array(y_coordinates)
        self.unique_x, self.x_index = np.unique(x_coordinates, return_inverse=True)
        self.unique_y, self.y_index = np.unique(y_coordinates, return_inverse=True)
        self.data_pivot = np.zeros((len(self.unique_y), len(self.unique_x)), dtype=float)
        self.data = np.array(list())
        self.data_x = np.array(list())
        self.data_y = np.array(list())
        self.data_z = np.array(list())
        self.x_label_idx = [0, len(self.unique_x) - 1]
        self.x_label_val = [np.round(self.unique_x[0], 3), np.round(self.unique_x[-1], 3)]
        self.y_label_idx = [0, len(self.unique_y) - 1]
        self.y_label_val = [np.round(self.unique_y[0], 3), np.round(self.unique_y[-1], 3)]
        self.x_axis_label = None
        self.y_axis_label = None
        self.bar_label = None
        self.bar_unit = None
        self.heading = None
        self.location_end = None
        self.limits = [None, None]
        self.norm_factor = float(1)
        self.normalise = False
        self.normalised_limits = [None, None]
