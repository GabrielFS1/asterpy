import rasterio
import numpy as np
from asterpy import histogram
import subprocess
from pathlib import Path
from typing import Union


def phyll_calc(filename: Union[str, Path], outpath: Union[str, Path]='', output_filename: str=''):
    """Calculates the phyllosilicate (Phyll) from a multiband raster image."""

    with rasterio.open(filename) as ds:
        band_10 = ds.read(1)
        band_11 = ds.read(2)
        band_12 = ds.read(3)

        meta = ds.profile
        meta['dtype'] = rasterio.float32 # Changes the data type to float32
        meta['count'] = 1 # Sets the bands numbers to one

    # Ignores invalid operations
    np.seterr(divide='ignore', invalid='ignore')

    phyllosilicates = band_10/band_11*band_12
    phyllosilicates = np.ma.masked_invalid(phyllosilicates)

    description = 'Band Math AST10/AST11*AST12'

    with rasterio.open(outpath + output_filename + '_Phyll.tif', 'w', **meta) as dataset:
        dataset.write(phyllosilicates.astype(rasterio.float32), 1)
        dataset.set_band_description(1, description)

def npv_calc(filename: Union[str, Path], outpath: Union[str, Path]='', output_filename: str=''):
    """Calculates the Non-Photosynthetic Vegetation (NPV) from a multiband raster image."""

    with rasterio.open(filename) as ds:
        band_11 = ds.read(2)
        band_13 = ds.read(4)
        band_14 = ds.read(5)

        meta = ds.profile
        meta['dtype'] = rasterio.float32 # Changes the data type to float32
        meta['count'] = 1 # Sets the bands numbers to one

    # Ignores invalid operations
    np.seterr(divide='ignore', invalid='ignore')

    npvthm = band_11/(band_13 + band_14)
    npvthm = np.ma.masked_invalid(npvthm)

    description = 'Band Math AST11/(AST13 + AST14)'

    with rasterio.open(outpath + output_filename + '_Npv.tif', 'w', **meta) as dataset:
        dataset.write(npvthm.astype(rasterio.float32), 1)
        dataset.set_band_description(1, description)

def qtz_calc(filename: Union[str, Path], outpath: Union[str, Path]='', output_filename: str=''):
    """Calculates the Quartz (Qtz) from a multiband raster image."""

    with rasterio.open(filename) as ds:
        band_10 = ds.read(1)
        band_11 = ds.read(2)
        band_12 = ds.read(3)
        band_13 = ds.read(4)

        meta = ds.profile
        meta['dtype'] = rasterio.float32 # Changes the data type to float32
        meta['count'] = 1 # Sets the bands numbers to one

    # Ignores invalid operations
    np.seterr(divide='ignore', invalid='ignore')

    quartz = band_11/(band_10 + band_12)*band_13/band_12
    quartz = np.ma.masked_invalid(quartz)

    description = 'Band Math AST11/(AST10 + AST12)*AST13/AST12'

    with rasterio.open(outpath + output_filename + '_Qtz.tif', 'w', **meta) as dataset:
        dataset.write(quartz.astype(rasterio.float32), 1)
        dataset.set_band_description(1, description)

