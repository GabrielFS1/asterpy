import os
import rasterio
from osgeo import gdal, ogr, osr

def layer_stack(file, path):
    layer_dir = path + '01_Layer_Stacking\\'
    files_dir = path + '00_Arquivos\\'
    
    print("Processando Layer Stacking...")
    # Cria lista com os caminhos de cada banda
    band_list = []
    band_files = os.listdir(files_dir + file)
    for i in band_files:
        # Verifica se o arquivo é .tif
        if i.split('.')[-1] != 'tif':
            continue
        else:
            # Garante que é o arquivo com a banda correta (10-14)
            if len(i.split('.')[2]) == 11 and i.split('.')[2][9] == '1' and i.split('.')[2][10] in '01234':
                band_list.append(files_dir + file + '\\' + i)

    # Lê os metadados do primeiro arquivo
    with rasterio.open(band_list[0]) as src0:
        meta = src0.meta

    # Atualiza numero de camadas e o tipo dos dados
    meta.update(count = len(band_list), dtype='uint16')

    descriptions = [
    'Band 10',
    'Band 11',
    'Band 12',
    'Band 13',
    'Band 14']

    # Lê cada camada do arquivo e escreve em um arquivo único
    with rasterio.open(layer_dir + file + '_Layer_Stacking_sem_rotacao.tif', 'w', **meta) as dst:
        for id, layer in enumerate(band_list, start=1):
            with rasterio.open(layer) as src1:
                dst.write_band(id, src1.read(1))
                # Adiciona descrição da banda de acordo com a lista descriptions
                dst.set_band_description(id, descriptions[id-1])

    # Rotaciona a imagem a partir dos metadados
    rotated_image = gdal.Warp(layer_dir + file + '_Layer_Stacking.tif', layer_dir + file + '_Layer_Stacking_sem_rotacao.tif')
    del rotated_image
    os.remove(layer_dir + file + '_Layer_Stacking_sem_rotacao.tif')
