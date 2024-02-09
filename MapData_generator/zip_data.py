import zlib
import bz2
import os


def zip_data(target, target_type='file_folder', method='zlib', output_path=None):
    '''
    Compress the data using zlib or bz2
    :param target: the file or folder to be compressed
    :param target_type: 'file' or 'file_folder'
    :param method: 'zlib' or 'bz2'
    :param output_path: the path to save the compressed file
    :return: the compressed data if target_type is 'file'
    '''
    if target_type == 'file_folder':
        if not output_path:
            raise ValueError('Output path must be provided for file_folder target_type')
        for filename in os.listdir(target):
            print('processing ', filename)
            file_path = os.path.join(target, filename)
            output_file_path = os.path.join(output_path, filename + ('.zlib' if method == 'zlib' else '.bz2'))
            with open(file_path, 'rb') as f:
                data = f.read()
            if method == 'zlib':
                compressed_data = zlib.compress(data)
            elif method == 'bz2':
                compressed_data = bz2.compress(data)
            else:
                raise ValueError('method is not supported')

            with open(output_file_path, 'wb') as f:
                f.write(compressed_data)

    elif target_type == 'file':
        with open(target, 'rb') as f:
            data = f.read()
        if method == 'zlib':
            compressed_data = zlib.compress(data)
        elif method == 'bz2':
            compressed_data = bz2.compress(data)
        else:
            raise ValueError('method is not supported')

        if output_path:
            with open(output_path, 'wb') as f:
                f.write(compressed_data)
        return compressed_data
    else:
        raise ValueError('target_type is not supported')


if __name__ == "__main__":
    zip_data(target='../USGS_GeoData_interp', target_type='file_folder', method='zlib',output_path='../USGS_GeoData_zipped')
    # zip_data(target='../USGS_GeoData_interp/AG100.v003.-01.0.-066.0.h5', target_type='file', method='zlib', output_path='../USGS_GeoData_zipped/AG100.v003.-01.0.-066.0.h5.zlib')
