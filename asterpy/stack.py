import os
from pathlib import Path
import rasterio
from osgeo import gdal, ogr, osr
from typing import List, Union

def layer_stack(bands: List[Path], output_filename: str, outpath: Union[str, Path]='') -> Path:
    """
    :param bands: A List of paths to the band files

    :return: The path to the generated file  """

    # Gets the metadata from the first image
    with rasterio.open(bands[0]) as ds:
        meta = ds.meta

    # Updates the layers number and the data type
    meta.update(count=len(bands), dtype='uint16')

    with rasterio.open(outpath + output_filename + '_Layer_Stacking_no_rotation.tif', 'w', **meta) as ds:
        for i, layer in enumerate(bands, start=1):
            with rasterio.open(layer) as src1:
                ds.write_band(i, src1.read(1))

    # Rotaciona a imagem a partir dos metadados
    gdal.Warp(outpath + output_filename + '_Layer_Stacking.tif', outpath + output_filename + '_Layer_Stacking_no_rotation.tif')
    os.remove(outpath + output_filename + '_Layer_Stacking_no_rotation.tif')

    return outpath + output_filename + '_Layer_Stacking.tif'
