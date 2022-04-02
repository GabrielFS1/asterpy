import subprocess
import cv2
import rasterio
import asterpy as ap
import sqlite3
import os
from osgeo import gdal
import numpy as np



# Gets the mean values (max and min of the database)
db = sqlite3.connect("aster_dados.db", uri=True)
rows = db.execute("SELECT * FROM aster_data").fetchall()



def normal_min_max_mean(index: int=5):
    sum = qtd = 0

    # Calculates the minimum value from the database
    for row in rows:
        if row[index]:
            sum += float(row[index].split(':')[0])
            qtd += 1
    min = sum / qtd

    sum = qtd = 0

    # Calculates the maximum value from the database
    for row in rows:
        if row[index]:
            sum += float(row[index].split(':')[1])
            qtd += 1
    max = sum / qtd

    return min, max


def day_min_max_mean(index: int=5):
    sum = qtd = 0

    # Calculates the minimum value from the database
    for row in rows:
        if row[index]:
            if row[4] == 'dia':
                sum += float(row[index].split(':')[0])
                qtd += 1
    min = sum / qtd

    sum = qtd = 0

    # Calculates the maximum value from the database
    for row in rows:
        if row[index]:
            if row[4] == 'dia':
                sum += float(row[index].split(':')[1])
                qtd += 1
    max = sum / qtd

    return min, max

def night_min_max_mean(index: int=5):
    sum = qtd = 0

    # Calculates the minimum value from the database
    for row in rows:
        if row[index]:
            if row[4] == 'noite':
                sum += float(row[index].split(':')[0])
                qtd += 1
    min = sum / qtd

    sum = qtd = 0

    # Calculates the maximum value from the database
    for row in rows:
        if row[index]:
            if row[4] == 'noite':
                sum += float(row[index].split(':')[1])
                qtd += 1
    max = sum / qtd

    return min, max



"""
index

5 - phyll
6 - npv
7 - qtz
"""
print(normal_min_max_mean(5))
print(day_min_max_mean(5))
print(night_min_max_mean(5))


files = os.listdir("00_Arquivos")

for file in files:

    if file.split('.')[-1] == 'zip':
        continue

    layer_dir = 'Teste\\'
    files_dir = '00_Arquivos\\'

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

    descriptions = ['Band 10', 'Band 11', 'Band 12', 'Band 13', 'Band 14']

    # Lê cada camada do arquivo e escreve em um arquivo único
    with rasterio.open(layer_dir + file + '_Layer_Stacking_sem_rotacao.tif', 'w', **meta) as dst:
        for id, layer in enumerate(band_list, start=1):
            with rasterio.open(layer) as src1:
                dst.write_band(id, src1.read(1))
                # Adiciona descrição da banda de acordo com a lista descriptions
                dst.set_band_description(id, descriptions[id-1])

    # Rotaciona a imagem a partir dos metadados
    rotated_image = gdal.Warp(layer_dir + file + '_Layer_Stacking.tif', layer_dir + file + '_Layer_Stacking_sem_rotacao.tif')
    os.remove(layer_dir + file + '_Layer_Stacking_sem_rotacao.tif')


    # === Generates the index images === #
    layer_dir = 'Teste\\'

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

    with rasterio.open("Teste\\" + file + '_Phyll.tif', 'w', **ras_meta) as dst1:
        # Define o array da banda como o array phyll
        dst1.write(phyllosilicates.astype(rasterio.float32), 1)
        dst1.set_band_description(1, descriptions[0]) # Escreve a descrição de cada banda

    with rasterio.open("Teste\\" + file + '_Npv.tif', 'w', **ras_meta) as dst1:
        # Define o array da banda como o array npv
        dst1.write(npvthm.astype(rasterio.float32), 1)
        # Escreve a descrição da banda
        dst1.set_band_description(1, descriptions[1])

    with rasterio.open("Teste\\" + file + '_Qtz.tif', 'w', **ras_meta) as dst1:
        # Define o array da banda como o array qtz
        dst1.write(quartz.astype(rasterio.float32), 1)
        # Escreve a descrição da banda
        dst1.set_band_description(1, descriptions[2])
    ds.close()


    # Shows the original image
    img_in = "Teste\\" + file + "_Phyll.tif"
    min, max = ap.histogram.get_histogram_range(img_in)
    subprocess.call(['gdal_translate.exe', '-ot', 'Byte', '-quiet', '-scale', str(min), str(max), img_in, "Teste\\" + file + "original_Phyll.tif"])


    #Gets the image period (day/night) to define the histogram value
    infos = file.split('_')[2]
    hour = int(infos[11:13])
    if hour >= 6 and hour < 18:
        period = 'dia'
        min, max = day_min_max_mean()
    else:
        period = 'noite'
        min, max = night_min_max_mean()

    # Makes the threshold clipping
    subprocess.call(['gdal_translate.exe', '-ot', 'Byte', '-quiet' ,'-scale', str(min), str(max), img_in, "Teste\\" + file + "processed_Phyll.tif"])

    #img_in = "Teste\\" + file + "_Npv"
    #min, max = ap.histogram.get_histogram_range("Teste\\" + file + '_Npv.tif')
    #subprocess.call(['gdal_translate.exe', '-ot', 'Byte', '-quiet', '-scale', str(min), str(max), img_in, index_dir_fig + dir + file + index])


    #img_in = "Teste\\" + file + "_Qtz"
    #min, max = ap.histogram.get_histogram_range("Teste\\" + file + '_Qtz.tif')
    #subprocess.call(['gdal_translate.exe', '-ot', 'Byte', '-quiet', '-scale', str(min), str(max), img_in, index_dir_fig + dir + file + index])


    img = cv2.imread("Teste\\" + file + "original_Phyll.tif")
    img2 = cv2.imread("Teste\\" + file + "processed_Phyll.tif")

    cv2.namedWindow(file + "_Original", cv2.WINDOW_NORMAL)
    cv2.namedWindow(file + "_Processed", cv2.WINDOW_NORMAL)

    cv2.imshow(file + "_Original", img)
    cv2.imshow(file + "_Processed", img2)

    cv2.waitKey()

    cv2.destroyAllWindows()