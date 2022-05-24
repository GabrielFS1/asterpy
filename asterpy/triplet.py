from pathlib import Path
from typing import List, Union
import rasterio

def triplet(red: Union[str, Path], green: Union[str, Path], blue: Union[str, Path], outfile: Union[str, Path]) -> Path:
    """

    :param red:
    :param green:
    :param blue:

    :return:
    """

    r_arr: List[List[float]] = rasterio.open(red).read(1)
    g_arr: List[List[float]] = rasterio.open(green).read(1)
    b_arr: List[List[float]] = rasterio.open(blue).read(1)

    files: List[Union[str, Path]] = [red, green, blue]

    # Soma cada pixels das três bandas
    sum_rgb: List[List[float]] = r_arr + g_arr + b_arr

    # Se a soma do pixel é maior que zero, atribui o valor 255
    sum_rgb[sum_rgb>0] = 255

    descriptions = [
    'Band Red',
    'Band Green',
    'Band Blue',
    'Band Alpha']

    # Gets the metadata from the first file
    with rasterio.open(red) as ds:
        meta = ds.meta

        # Atualiza numero de camadas e o tipo dos dados
        meta.update(count=4, interleave='band', compress='lzw')

    # Le cada camada do arquivo e escreve em um arquivo único
    with rasterio.open(outfile, 'w', **meta) as ds:
        for id, layer in enumerate(files, start=1):
            with rasterio.open(layer) as src1:
                ds.write_band(id, src1.read(1))
                ds.set_band_description(id, descriptions[id-1])
        ds.write_band(4, sum_rgb)
        ds.set_band_description(4, descriptions[3])
