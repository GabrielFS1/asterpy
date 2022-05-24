from pathlib import Path
from typing import Union
import rasterio
import numpy as np
from asterpy import histogram
import subprocess

def phyll_calc(infile: Union[str, Path], outfile: Union[str, Path]) -> Path:
    """Calculation of the thermal index of phyllosilicates (Vicente & Souza Filho, 2010) - AST10/AST11*AST12

    :param filename: The path to a multiband raster file
    :param output_filename: The name of the generated file
    :param outpath: The path where the generated image is going to be saved

    :return: The path to the generated image """

    with rasterio.open(infile) as original_ds:
        band10 = original_ds.read(1).astype(float)
        band11 = original_ds.read(2).astype(float)
        band12 = original_ds.read(3).astype(float)

        # Gets the metadata of the original file
        # Updates the metadata for the new image
        meta = original_ds.profile
        meta['dtype'] = rasterio.float32
        meta['count'] = 1

    # Ignores invalid operations
    np.seterr(divide='ignore', invalid='ignore')

    phyllosilicates = band10/band11*band12
    phyllosilicates = np.ma.masked_invalid(phyllosilicates)

    with rasterio.open(outfile, 'w', **meta) as ds:
        ds.write(phyllosilicates.astype(rasterio.float32), 1)
        ds.set_band_description(1, "Band Math AST10/AST11*AST12")

    return outfile


def npv_calc(infile: Union[str, Path], outfile: Union[str, Path]) -> Path:
    """Calculation of the thermal index of non-photosynthetically active vegetation (Vicente et al., 2017) - AST11/(AST13 + AST14)

    :param filename: The path to a multiband raster file
    :param output_filename: The name of the generated file
    :param outpath: The path where the generated image is going to be saved

    :return: The path to the generated image """

    with rasterio.open(infile) as original_ds:
        band11 = original_ds.read(2).astype(float)
        band13 = original_ds.read(4).astype(float)
        band14 = original_ds.read(5).astype(float)

        # Gets the metadata of the original file
        # Updates the metadata for the new image
        meta = original_ds.profile
        meta['dtype'] = rasterio.float32
        meta['count'] = 1

    # Ignores invalid operations
    np.seterr(divide='ignore', invalid='ignore')

    npvthm = band11/(band13 + band14)
    npvthm = np.ma.masked_invalid(npvthm)

    with rasterio.open(outfile, 'w', **meta) as ds:
        ds.write(npvthm.astype(rasterio.float32), 1)
        ds.set_band_description(1, 'Band Math AST11/(AST13 + AST14)')

    return outfile


def qtz_calc(infile: Union[str, Path], outfile: Union[str, Path]) -> Path:
    """Calculation of the thermal index of quartz (Rockwell & Hofstra, 2008) - AST11/(AST10 + AST12)*AST13/AST12

    :param filename: The path to a multiband raster file
    :param output_filename: The name of the generated file
    :param outpath: The path where the generated image is going to be saved

    :return: The path to the generated image """

    with rasterio.open(infile) as original_ds:
        band10 = original_ds.read(1).astype(float)
        band11 = original_ds.read(2).astype(float)
        band12 = original_ds.read(3).astype(float)
        band13 = original_ds.read(4).astype(float)

        # Gets the metadata of the original file
        # Updates the metadata for the new image
        meta = original_ds.profile
        meta['dtype'] = rasterio.float32
        meta['count'] = 1

    # Ignores invalid operations
    np.seterr(divide='ignore', invalid='ignore')

    quartz = band11/(band10 + band12)*band13/band12
    quartz = np.ma.masked_invalid(quartz)

    with rasterio.open(outfile, 'w', **meta) as ds:
        ds.write(quartz.astype(rasterio.float32), 1)
        ds.set_band_description(1, 'Band Math AST11/(AST10 + AST12)*AST13/AST12')

    return outfile

def generate_index_image(file, path):
    phyll_dir = path + '01_Phyll\\'
    npv_dir = path + '02_Npv\\'
    qtz_dir = path + '03_Qtz\\'
    
    index_dir = path + '02_Indices\\'
    index_dir_fig = path + '02_Indices\\Figuras\\'

    for i in range(0, 3):
        if i == 0:
            dir = phyll_dir
            index = '_Phyll.tif'

        elif i == 1:
            dir = npv_dir
            index = '_Npv.tif'

        elif i == 2:
            dir = qtz_dir
            index = '_Qtz.tif'

        img_in = index_dir + dir + file + index

        min, max = histogram.get_histogram_range(img_in)
        subprocess.call(['gdal_translate.exe', '-ot', 'Byte', '-quiet', '-scale', str(min), str(max), img_in, index_dir_fig + dir + file + index])