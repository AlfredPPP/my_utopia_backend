import h5py
import flask
import numpy
import os

from scipy.interpolate import interp1d


# read the coordinate and create a hdf5 file of a proper area with player in its center


def choose_dataset(path: str, temp_coordinate: list) -> str:
    """
        return the path of file which contains the player's coordinate

        Args:
            path (str): HDF5 file path
            temp_coordinate (list): player's coordinate

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


def interpolate_array(array_1:list, array_2:list):
    pass

if __name__ == "__main__":
    # unity terrain data
    map_size = 10000

    # temp var should be deleted later
    temp_coordinate = [-1.5575576, -66.49149]

    work_dir = os.path.dirname(os.path.dirname(__file__))
    choose_dataset(os.path.join(work_dir, 'USGS_GeoData\\AG100.v003.-01.-067.0001.h5'), temp_coordinate)

