import os
import h5py
import numpy as np
from pykrige.ok import OrdinaryKriging
from scipy.interpolate import griddata


def interpolate_geodata(dataset, scale_factor: int) -> list:
    """
    Interpolates a geographic data matrix.

    :param dataset: HDF5 dataset.
    :param scale_factor:  The factor by which to increase the resolution of the data.
    :return: An array representing the interpolated data matrix.
    """

    # Convert data_matrix to numpy array if it's not already
    data_matrix = np.array(dataset)

    data_type = dataset.name

    # Get original dimensions
    original_height, original_width = data_matrix.shape

    # Generate grid points
    x = np.linspace(0, original_width - 1, original_width)
    y = np.linspace(0, original_height - 1, original_height)

    X, Y = np.meshgrid(x, y)

    # Flatten the grid points
    points = np.vstack([X.ravel(), Y.ravel()]).T

    X_flat = X.flatten()
    Y_flat = Y.flatten()

    # New grid points for interpolation
    x_new = np.linspace(0, original_width - 1 / scale_factor, original_width * scale_factor)
    y_new = np.linspace(0, original_height - 1 / scale_factor, original_height * scale_factor)

    X_new, Y_new = np.meshgrid(x_new, y_new)

    if 'LWmap' not in data_type:
        # Perform Kriging interpolation for DEM data
        OK = OrdinaryKriging(X_flat, Y_flat, data_matrix.flatten(), variogram_model='hole-effect', verbose=False,
                             enable_plotting=False)
        z_new, ss = OK.execute('grid', x_new, y_new)
        interpolated_matrix = z_new.data
    else:
        # Perform Nearest Neighbor interpolation for Hydrological data
        interpolated_matrix = griddata(points, data_matrix.ravel(), (X_new, Y_new), method='nearest')

    return interpolated_matrix


def process_and_save_h5_file(file_path, output_folder):
    # Directory paths
    filename = os.path.basename(file_path)
    output_file_path = os.path.join(output_folder, filename)

    with h5py.File(file_path, 'r') as file:
        with h5py.File(output_file_path, 'w') as output_file:
            for group_name in file:
                group = file[group_name]
                if group_name not in ('ASTER GDEM', 'Geolocation', 'Land Water Map', 'NDVI'):
                    continue
                for dataset_name in group:
                    processed_data = interpolate_geodata(group[dataset_name], 100)
                    output_file.create_group(group_name)
                    output_file[group_name].create_dataset("dataset_name", data=processed_data)


if __name__ == "__main__":
    input_folder = '../USGS_GeoData_ori'
    output_folder = '../USGS_GeoData_interp'
    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)
        process_and_save_h5_file(file_path, output_folder)
    process_and_save_h5_file(file_path, output_folder)
