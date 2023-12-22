import h5py
import numpy as np
import os
from flask import Flask
from pykrige.ok import OrdinaryKriging
from scipy.interpolate import griddata

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


# A global dictionary to store processed data
processed_data = {}

@app.route('/<section>', methods=['GET'])
def post_data(section: str):
    # Return the processed data for the requested section
    section = section.replace('-', '/').replace('_', ' ')
    data = processed_data.get(section, {})
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

    # Flatten the grid points
    points = np.vstack([X.ravel(), Y.ravel()]).T

    X_flat = X.flatten()
    Y_flat = Y.flatten()

    # New grid points for interpolation
    x_new = np.linspace(0, original_width - 1/scale_factor, original_width * scale_factor)
    y_new = np.linspace(0, original_height - 1/scale_factor, original_height * scale_factor)

    X_new, Y_new = np.meshgrid(x_new, y_new)


    if data_type == 'DEM':
        # Perform Kriging interpolation for DEM data
        OK = OrdinaryKriging(X_flat, Y_flat, data_matrix.flatten(), variogram_model='spherical', verbose=False,
                             enable_plotting=False)
        z_new, ss = OK.execute('grid', x_new, y_new)
        interpolated_matrix = z_new.data

    elif data_type == 'Hydro':
        # Perform Nearest Neighbor interpolation for Hydrological data
        interpolated_matrix = griddata(points, data_matrix.ravel(), (X_new, Y_new), method='nearest')

    else:
        raise ValueError("Invalid data type. Choose 'DEM' or 'Hydro'.")

    return interpolated_matrix.tolist()


if __name__ == "__main__":

    # unity terrain data
    map_size = 1000

    # temp var should be deleted later, this coordinate should be uploaded from flutter
    temp_coordinate = [-1.5575576, -66.49149]

    work_dir = os.path.dirname(os.path.dirname(__file__))
    path = choose_dataset(os.path.join(work_dir, 'USGS_GeoData\\AG100.v003.-01.-067.0001.h5'))
    for name in ['ASTER GDEM/ASTGDEM', 'NDVI/Mean', 'Land Water Map/LWmap']:
        data = select_data(path, name, map_size, temp_coordinate)
        data_type = 'Hydro' if 'Water' in name else 'DEM'
        terrain_data = interpolate_geodata(data_matrix=data, scale_factor=10, data_type=data_type)

        # Store processed data in the global dictionary
        processed_data[name] = terrain_data

        # Start the Flask app
    app.run(debug=True, port=5002, use_reloader=False)
