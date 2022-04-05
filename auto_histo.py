import glob
import shutil
import subprocess
import cv2
import rasterio
import asterpy as ap
import sqlite3
import os
from osgeo import gdal
import numpy as np
from PIL import Image


# Gets the mean values (max and min of the database)
db = sqlite3.connect("aster_dados.db", uri=True)
rows = db.execute("SELECT * FROM aster_data").fetchall()


"""
def normal_min_max_mean(type: str='phyll'):
    if type not in ['phyll', 'npv', 'qtz']:
        raise ValueError("O tipo específicado não é valido (phyll, npv ou qtz)")

    sum = qtd = 0

    if type == 'phyll':
        index = 5
    elif type == 'npv':
        index = 6
    elif type == 'qtz':
        index = 7

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
"""

def get_min_max(type: str='phyll', period: str='dia'):

    if type not in ['phyll', 'npv', 'qtz']:
        raise ValueError(f"O tipo específicado não é valido. O valor deve ser ['phyll', 'npv', 'qtz']")

    if period not in ['dia', 'noite']:
        raise ValueError(f"O valor específicado {period} não é valido. O valor deve ser ['dia', 'noite']")

    sum_min = sum_max = qtd = 0

    # Sets index with the index number of the column in the database
    if type == 'phyll':
        index = 5
    elif type == 'npv':
        index = 6
    elif type == 'qtz':
        index = 7

    # Calculates the minimum value from the database
    for row in rows:
        if row[index]:
            if row[4] == period:
                sum_min += float(row[index].split(':')[0]) 
                sum_max += float(row[index].split(':')[1]) 
                qtd += 1
    return sum_min / qtd, sum_max / qtd


"""
index

5 - phyll
6 - npv
7 - qtz
"""
print(f"Phyll day: {get_min_max()}")
print(f"Npv day: {get_min_max('npv', 'dia')}")
print(f"Qtz day: {get_min_max('qtz', 'dia')}")
print(f"Phyll night: {get_min_max('phyll', 'noite')}")
print(f"Npv night: {get_min_max('npv', 'noite')}")
print(f"Qtz night: {get_min_max('qtz', 'noite')}")


files = os.listdir("00_Arquivos")

control = 0

for i in range(len(files)):
    file = files[i]
    print(file)
    print(f"control: {control}")
    # Checks if the image period is day or night
    #Gets the image period (day/night) to define the histogram value
    infos = file.split('_')[2]
    hour = int(infos[11:13])
    if hour >= 6 and hour < 18:
        period = 'dia'
    else:
        period = 'noite'

    if control == 0:
        type = 'Phyll'
        min, max = get_min_max('phyll', period)
    elif control == 1:
        type = 'Npv'
        min, max = get_min_max('npv', period)
    elif control == 2:
        type = 'Qtz'
        min, max = get_min_max('qtz', period)


    if file.split('.')[-1] == 'zip' or file.split('.')[-1]  == 'met':
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

    descriptions = [
    'Band Math AST10/AST11*AST12', # Descrição filossilicatos
    'Band Math AST11/(AST13 + AST14)', # Descrição npvthm
    'Band Math AST11/(AST10 + AST12)*AST13/AST12'] # Descrição quartzo

    # Altera os metadados da imagem para float e determina 1 banda para a imagem
    ras_meta['dtype'] = rasterio.float32
    ras_meta['count'] = 1

    if control == 0:
        # Cálculo do índice termal de filossilicatos (Vicente & Souza Filho, 2010)
        phyllosilicates = AST10/AST11*AST12
        phyllosilicates = np.ma.masked_invalid(phyllosilicates)
        with rasterio.open("Teste\\" + file + '_Phyll.tif', 'w', **ras_meta) as dst1:
            # Define o array da banda como o array phyll
            dst1.write(phyllosilicates.astype(rasterio.float32), 1)
            dst1.set_band_description(1, descriptions[0]) # Escreve a descrição de cada banda

    elif control == 1:
        # Cálculo do índice termal de vegetação não fotossinteticamente ativa (Vicente et al., 2017)
        npvthm = AST11/(AST13 + AST14)
        npvthm = np.ma.masked_invalid(npvthm)
        with rasterio.open("Teste\\" + file + '_Npv.tif', 'w', **ras_meta) as dst1:
            # Define o array da banda como o array npv
            dst1.write(npvthm.astype(rasterio.float32), 1)
            # Escreve a descrição da banda
            dst1.set_band_description(1, descriptions[1])

    elif control == 2:
        # Cálculo do índice termal de quartzo (Rockwell & Hofstra, 2008)
        quartz = AST11/(AST10 + AST12)*AST13/AST12
        quartz = np.ma.masked_invalid(quartz)
        with rasterio.open("Teste\\" + file + '_Qtz.tif', 'w', **ras_meta) as dst1:
            # Define o array da banda como o array qtz
            dst1.write(quartz.astype(rasterio.float32), 1)
            # Escreve a descrição da banda
            dst1.set_band_description(1, descriptions[2])

    ds.close()

    # Shows the original image
    img_in = f"Teste\\{file}_{type}.tif"
    min, max = ap.histogram.get_histogram_range(img_in)
    subprocess.call(['gdal_translate.exe', '-ot', 'Byte', '-quiet', '-scale', str(min), str(max), img_in, f"Teste\\{file}original_{type}.tif"])

    # Makes the threshold clipping
    subprocess.call(['gdal_translate.exe', '-ot', 'Byte', '-quiet' ,'-scale', str(min), str(max), img_in, f"Teste\\{file}processed_{type}.tif"])

    img = cv2.imread(f"Teste\\{file}original_{type}.tif")
    img2 = cv2.imread(f"Teste\\{file}processed_{type}.tif")

    # Apllies the median filter
    #img2 = cv2.medianBlur(img2, 3)

    cv2.namedWindow(file + "_Original", cv2.WINDOW_NORMAL)
    cv2.namedWindow(file + "_Processed", cv2.WINDOW_NORMAL)

    cv2.imshow(file + "_Original", img)
    cv2.imshow(file + "_Processed", img2)

    # Tries to open the image manually processed
    try:
        im = Image.open(f"03_Histograma\\0{control + 1}_{type}\\{file}_Histo_{type}.tif")
        im.show()

    except FileExistsError:
        pass

    cv2.waitKey()

    cv2.destroyAllWindows()

    folder = 'Teste\\'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            #print('Failed to delete %s. Reason: %s' % (file_path, e))
            pass

    control += 1
