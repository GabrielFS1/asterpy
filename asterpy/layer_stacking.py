import os
from pathlib import Path
import rasterio
from osgeo import gdal, ogr, osr
from typing import List, Union
from tempfile import NamedTemporaryFile

def layer_stack(bands: List[Path], outfile: Union[str, Path]) -> Path:
    """
    :param bands: A List of paths to the band files

    :return: The path to the generated file  """

    # Gets the metadata from the first image
    with rasterio.open(bands[0]) as ds:
        meta = ds.meta

    # Updates the layers number and the data type
    meta.update(count=len(bands), dtype='uint16')

    tempfile = NamedTemporaryFile(suffix='.tif').name

    with rasterio.open(tempfile, 'w', **meta) as ds:
        for i, layer in enumerate(bands, start=1):
            with rasterio.open(layer) as src1:
                ds.write_band(i, src1.read(1))

    # Rotaciona a imagem a partir dos metadados
    gdal.Warp(outfile, tempfile)

    # Remove the temp file
    os.unlink(tempfile)
    assert not os.path.exists(tempfile)

    return outfile
