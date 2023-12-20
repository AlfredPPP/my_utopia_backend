import h5py
import numpy as np
import os
from flask import Flask
from pykrige.ok import OrdinaryKriging
from scipy.interpolate import interp2d

# read the coordinate and create a hdf5 file of a proper area with player in its center

app = Flask(__name__)


def choose_dataset(path: str) -> str:
    """
        return the path of file which contains the player's coordinate

        Args:
            path (str): HDF5 file path

        Returns:
            str: file path

        ps: this method could be replaced by querying database once the coordinate-hdf5file relation setup
    """
    with h5py.File(path, 'r') as file:
        latitude_array = file['Geolocation']['Latitude'][:, 0]
        longitude_array = file['Geolocation']['Longitude'][0, :]
        if latitude_array[0] >= temp_coordinate[0] >= latitude_array[-1]:
            if longitude_array[0] <= temp_coordinate[1] <= longitude_array[-1]:
                return path
        else:
            return ''


def select_data(dataset_path: str, group_path: str, size: int, coordinate: list):
    player_latitude, player_longitude = coordinate
    with h5py.File(dataset_path, 'r') as file:
        latitude = file['Geolocation']['Latitude'][:, 0]
        longitude = file['Geolocation']['Longitude'][0, :]
        data = file[group_path]

        # Convert latitude and longitude to index
        lat_index = np.argmin(np.abs(latitude - player_latitude))
        lon_index = np.argmin(np.abs(longitude - player_longitude))

        # Calculate the range to select
        lat_start = max(0, lat_index - size // 200)
        lat_end = min(lat_start + size // 100, latitude.shape[0])
        lon_start = max(0, lon_index - size // 200)
        lon_end = min(lon_start + size // 100, longitude.shape[0])

        # Select the data
        return data[lat_start:lat_end, lon_start:lon_end]


@app.route('/<section>', methods=['GET'])
def post_data(section: str, data):
    return data


def interpolate_geodata(data_matrix, scale_factor: int, data_type: str) -> list:
    """
    Interpolates a geographic data matrix.

    :param data_matrix: A 2D list or array of geographic data.
    :param scale_factor:  The factor by which to increase the resolution of the data.
    :param data_type: Type of data, 'DEM' for elevation data or 'Hydro' for water presence data.
    :return: A list representing the interpolated data matrix.
    """

    # Convert data_matrix to numpy array if it's not already
    data_matrix = np.array(data_matrix)

    # Get original dimensions
    original_height, original_width = data_matrix.shape

    # Generate grid points
    x = np.linspace(0, original_width - 1, original_width)
    y = np.linspace(0, original_height - 1, original_height)

    X, Y = np.meshgrid(x, y)

    X_flat = X.flatten()
    Y_flat = Y.flatten()

    # New grid points for interpolation
    x_new = np.linspace(0, original_width - 1, original_width * scale_factor)
    y_new = np.linspace(0, original_height - 1, original_height * scale_factor)

    X_new, Y_new = np.meshgrid(x_new, y_new)

    X_new_flat = X_new.flatten()
    Y_new_flat = Y_new.flatten()

    if data_type == 'DEM':
        # Perform Kriging interpolation for DEM data
        OK = OrdinaryKriging(X_flat, Y_flat, data_matrix.flatten(), variogram_model='linear', verbose=False,
                             enable_plotting=False)
        z_new, ss = OK.execute('grid', x_new, y_new)
        interpolated_matrix = z_new.data

    elif data_type == 'Hydro':
        # Perform Nearest Neighbor interpolation for Hydrological data
        interp_func = interp2d(x, y, data_matrix, kind='nearest')
        interpolated_matrix = interp_func(x_new, y_new)

    else:
        raise ValueError("Invalid data type. Choose 'DEM' or 'Hydro'.")

    return interpolated_matrix.tolist()


if __name__ == "__main__":
    # app.run(debug=True)

    # unity terrain data
    map_size = 10000

    # temp var should be deleted later
    temp_coordinate = [-1.5575576, -66.49149]

    work_dir = os.path.dirname(os.path.dirname(__file__))
    path = choose_dataset(os.path.join(work_dir, 'USGS_GeoData\\AG100.v003.-01.-067.0001.h5'))
    for name in ['ASTER GDEM/ASTGDEM', 'NDVI/Mean', 'Land Water Map/LWmap']:
        data = select_data(path, name, map_size, temp_coordinate)
        data_type = 'Hydro' if 'Water' in name else 'DEM'
        terrain_data = interpolate_geodata(data_matrix=data, scale_factor=100, data_type=data_type)
        post_data(name, terrain_data)
