import rasterio
import numpy as np
from asterpy import histogram
import subprocess

def index_calc(file, path):
    phyll_dir = '01_Phyll\\'
    npv_dir = '02_Npv\\'
    qtz_dir = '03_Qtz\\'

    layer_dir = path + '01_Layer_Stacking\\'

    index_dir = path + '02_Indices\\'

    print("Processando Índices...")

    ds = rasterio.open(layer_dir + file + '_Layer_Stacking.tif')

    # Le cada banda do arquivo raster layer stack
    AST10 = ds.read(1).astype(float)
    AST11 = ds.read(2).astype(float)
    AST12 = ds.read(3).astype(float)
    AST13 = ds.read(4).astype(float)
    AST14 = ds.read(5).astype(float)

    # Lê os metadados do arquivo original
    ras_meta = ds.profile

    # Ignora operações inválidas
    np.seterr(divide='ignore', invalid='ignore')

    # Cálculo do índice termal de filossilicatos (Vicente & Souza Filho, 2010)
    phyllosilicates = AST10/AST11*AST12
    phyllosilicates = np.ma.masked_invalid(phyllosilicates)

    # Cálculo do índice termal de vegetação não fotossinteticamente ativa (Vicente et al., 2017)
    npvthm = AST11/(AST13 + AST14)
    npvthm = np.ma.masked_invalid(npvthm)

    # Cálculo do índice termal de quartzo (Rockwell & Hofstra, 2008)
    quartz = AST11/(AST10 + AST12)*AST13/AST12
    quartz = np.ma.masked_invalid(quartz)

    # Altera os metadados da imagem para float e determina 1 banda para a imagem
    ras_meta['dtype'] = rasterio.float32
    ras_meta['count'] = 1

    descriptions = [
    'Band Math AST10/AST11*AST12', # Descrição filossilicatos
    'Band Math AST11/(AST13 + AST14)', # Descrição npvthm
    'Band Math AST11/(AST10 + AST12)*AST13/AST12'] # Descrição quartzo

    for i in range(0, 3):
        if i == 0:
            with rasterio.open(index_dir + phyll_dir + file + '_Phyll.tif', 'w', **ras_meta) as dst1:
                # Define o array da banda como o array phyll
                dst1.write(phyllosilicates.astype(rasterio.float32), 1)
                dst1.set_band_description(1, descriptions[0]) # Escreve a descrição de cada banda
        
        if i == 1:
            with rasterio.open(index_dir + npv_dir + file + '_Npv.tif', 'w', **ras_meta) as dst1:
                # Define o array da banda como o array npv
                dst1.write(npvthm.astype(rasterio.float32), 1)
                # Escreve a descrição da banda
                dst1.set_band_description(1, descriptions[1])
       
        if i == 2:
            with rasterio.open(index_dir + qtz_dir + file + '_Qtz.tif', 'w', **ras_meta) as dst1:
                # Define o array da banda como o array qtz
                dst1.write(quartz.astype(rasterio.float32), 1)
                # Escreve a descrição da banda
                dst1.set_band_description(1, descriptions[2])
    ds.close()

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