from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List, Union
import matplotlib.pyplot as plt
import matplotlib
import rasterio
import os
from osgeo import gdal



def color_mapping(infile: Union[str, Path], outfile: Union[str, Path]) -> Path:
    # Colormap rainbow https://stackoverflow.com/questions/34768717/matplotlib-unable-to-save-image-in-same-resolution-as-original-image
    rainbow = {'red': ((0.0, 0.0, 0.0),
                (0.1, 0.5, 0.5),
                (0.2, 0.0, 0.0),
                (0.4, 0.2, 0.2),
                (0.6, 0.0, 0.0),
                (0.8, 1.0, 1.0),
                (1.0, 1.0, 1.0)),
        'green':((0.0, 0.0, 0.0),
                (0.1, 0.0, 0.0),
                (0.2, 0.0, 0.0),
                (0.4, 1.0, 1.0),
                (0.6, 1.0, 1.0),
                (0.8, 1.0, 1.0),
                (1.0, 0.0, 0.0)),
        'blue': ((0.0, 0.0, 0.0),
                (0.1, 0.5, 0.5),
                (0.2, 1.0, 1.0),
                (0.4, 1.0, 1.0),
                (0.6, 0.0, 0.0),
                (0.8, 0.0, 0.0),
                (1.0, 0.0, 0.0))}

    my_cmap = matplotlib.colors.LinearSegmentedColormap('my_colormap',rainbow,256)

    tempfile = NamedTemporaryFile(suffix='.tif').name

    dpi = 80

    im_data = plt.imread(infile)
    height, width = im_data.shape

    # Define o tamanho da figura de acordo com o tamanho imagem
    figsize = width / float(dpi), height / float(dpi)

    # Cria a figura no tamanho correto
    fig = plt.figure(figsize=figsize)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off') # Esconde as informações dos eixos

    # Aplica o color mapping a imagem
    im = ax.imshow(im_data, interpolation='nearest', aspect='auto', cmap=my_cmap)

    # Saves the RGB image without the metadata in a temporary file
    fig.savefig(tempfile, dpi=dpi)

    # Gets the metadata from the original file
    with rasterio.open(infile) as original_ds:
        meta = original_ds.profile
        meta['count'] = 4

    # Gets the bands of the RGB image to write the metadata
    with gdal.Open(tempfile) as dataset_rgb:
        r = dataset_rgb.GetRasterBand(1).ReadAsArray()
        g = dataset_rgb.GetRasterBand(2).ReadAsArray()
        b = dataset_rgb.GetRasterBand(3).ReadAsArray()

        sum_rgb: List[List[float]] = r + g + b

        # Verifica a partir da soma das três bandas, se houver qualquer dados em qualquer banda, define como 255 (opaco)
        sum_rgb[sum_rgb>0] = 255

        descriptions = [
        'Band Red',
        'Band Green',
        'Band Blue',
        'Band Alpha']

        # Insere as bandas em uma imagem com os metadados
        with rasterio.open(outfile, 'w', **meta) as ds:
            for i in range (1, 3 + 1):
                ds.write_band(i, dataset_rgb.GetRasterBand(i).ReadAsArray())
                ds.set_band_description(i, descriptions[i-1])
            # Alpha band to set the transparency in each pixel
            ds.write_band(4, sum_rgb)
            ds.set_band_description(4, descriptions[3])

    plt.close('all')
    return outfile
