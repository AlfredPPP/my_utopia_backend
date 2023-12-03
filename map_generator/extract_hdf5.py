import h5py
import os


def read_group(path: str,):

    with h5py.File(path, 'r') as file:
        for group in file.keys():
            data = file[group][...]
            with open(f'{group}.csv', 'w') as f:
                pass
# what format will unity need???

if __name__ == "__main__":
    work_dir = os.path.dirname(os.path.dirname(__file__))
    read_group(os.path.join(work_dir,'USGS_GeoData\\AG100.v003.-01.-035.0001.h5'))
    print(work_dir)
