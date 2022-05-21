import os
import rasterio
from osgeo import gdal
from typing import Union, List
from pathlib import Path

def layer_stack(bands: List[Union[str, Path]], outpath: Union[str, Path]='', output_filename: str=''):
    """
    :param bands: A List of band files to create the layer stack
    """

    for band in bands:
        if not band.endswith(('.tif')):
            return ValueError("File must be a GeoTIFF")


    # Checks the metadata of the first band file
    with rasterio.open(bands[0]) as src0:
        meta = src0.meta

    # Updates the number of layers and the datatype
    meta.update(count = len(bands), dtype = 'uint16')

    with rasterio.open(outpath + output_filename + '_Layer_Stacking_no_rotation.tif', 'w', **meta) as dst:
        for i, band in enumerate(bands, start=1):
            with rasterio.open(band) as src1:
                dst.write_band(i, src1.read(1))
                dst.set_band_description(i, "band" + i)

    # Rotates the image if it has the indication in the metadata
    gdal.Warp(outpath + output_filename + '_Layer_Stacking.tif', outpath + output_filename + '_Layer_Stacking_no_rotation.tif')

    try:
        os.remove(outpath + output_filename + '_Layer_Stacking_no_rotation.tif')
    except OSError:
        pass
