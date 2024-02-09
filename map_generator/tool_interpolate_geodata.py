import os
import h5py
import numpy as np
from datetime import datetime
from scipy.ndimage import zoom
from scipy.interpolate import griddata


def quadratic_interpolate(matrix, scale_factor):
    # Use scipy's zoom function with order=2 for bicubic interpolation
    return zoom(matrix, scale_factor, order=2)

def bilinear_interpolate(matrix, scale_factor):
    # Use scipy's zoom function with order=2 for bicubic interpolation
    return zoom(matrix, scale_factor, order=1)

def nearest_neighbor_interpolate(matrix, scale_factor):
    # Use scipy's zoom function with order=2 for bicubic interpolation
    return zoom(matrix, scale_factor, order=0)


def split_and_process_hdf5(filepath, output_folder):
    # filename should look like 'AG100.v003.-01.-066'
    filename = filepath[filepath.find('AG100'):-8]

    # Open the HDF5 file
    with h5py.File(filepath, 'r') as file:
        # Read datasets
        aster_gdem = file['ASTER GDEM']['ASTGDEM'][:]
        geo_lat = file['Geolocation']['Latitude'][:]
        geo_lon = file['Geolocation']['Longitude'][:]
        land_water_map = file['Land Water Map']['LWmap'][:]
        ndvi = file['NDVI']['Mean'][:]

        # Split each dataset into 10x10 sub-datasets of size 100x100
        for i in range(100):
            for j in range(100):
                # Calculate the start and end indices for slicing
                start_i, end_i = i * 10, (i + 1) * 10
                start_j, end_j = j * 10, (j + 1) * 10

                # Extract sub-datasets
                sub_aster_gdem = aster_gdem[start_i:end_i, start_j:end_j]
                sub_geo_lat = geo_lat[start_i:end_i, start_j:end_j]
                sub_geo_lon = geo_lon[start_i:end_i, start_j:end_j]
                sub_land_water_map = land_water_map[start_i:end_i, start_j:end_j]
                sub_ndvi = ndvi[start_i:end_i, start_j:end_j]

                # Process each sub-dataset
                sub_aster_gdem = quadratic_interpolate(sub_aster_gdem, 100)
                sub_geo_lat = bilinear_interpolate(sub_geo_lat, 100)
                sub_geo_lon = bilinear_interpolate(sub_geo_lon, 100)
                sub_land_water_map = nearest_neighbor_interpolate(sub_land_water_map, 100)
                sub_ndvi = quadratic_interpolate(sub_ndvi, 100)

                # Create a new HDF5 file for each 100x100 sub-dataset
                # sub_filename should look like 'AG100.v003.-01.01.-066.05.h5'
                sub_filename = filename[:15] + f'{i}.' + filename[15:19] + f'.{j}.h5'
                print(
                    f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}---> start saving {sub_filename}...remaining {10000 - i * 100 - j} tasks')
                output_path = os.path.join(output_folder, sub_filename)
                with h5py.File(output_path, 'w') as sub_file:
                    sub_file.create_dataset('ASTER GDEM/ASTGDEM', data=sub_aster_gdem)
                    sub_file.create_dataset('Geolocation/Latitude', data=sub_geo_lat)
                    sub_file.create_dataset('Geolocation/Longitude', data=sub_geo_lon)
                    sub_file.create_dataset('Land Water Map/LWmap', data=sub_land_water_map)
                    sub_file.create_dataset('NDVI/Mean', data=sub_ndvi)


if __name__ == "__main__":
    input_folder = '../USGS_GeoData_ori'
    output_folder = '../USGS_GeoData_interp'
    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)
        print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}---> start processing {file_path}......')
        split_and_process_hdf5(file_path, output_folder)
        break
