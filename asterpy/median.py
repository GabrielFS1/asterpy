import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Union
import cv2 as cv2
import rasterio

def median_filter(infile: Union[str, Path], outfile: Union[str, Path]) -> Path:
    # Abre a imagem com o opencv em modo escala de cinza
    img_median = cv2.imread(infile, 0)
    img_median = cv2.medianBlur(img_median, 3)

    tempfile = NamedTemporaryFile(suffix='.tif').name

    cv2.imwrite(tempfile, img_median)

    # Abre o arquivo do histograma para obter os metadados
    with rasterio.open(infile) as ds:
        meta = ds.profile

    # Abre imagem da mediana sem metadados para ler o array
    with rasterio.open(tempfile) as ds1:
        # Armazena o array da imagem com filtro mediana
        array = ds1.read(1)

    # Salva imagem com filtro mediana incluindo os metadados da imagem original
    with rasterio.open(outfile, 'w', **meta) as dts:
        dts.write_band(1, array)

    # Remove the temp file
    os.unlink(tempfile)
    assert not os.path.exists(tempfile)

    return outfile