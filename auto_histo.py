from calendar import month
import glob
import shutil
import subprocess
from typing import List
import cv2
import rasterio
import asterpy as ap
import sqlite3
import os
from osgeo import gdal
import numpy as np
from PIL import Image
import statistics


def get_min_max(type: str=None, period: str=None, months: str=None):
    db = sqlite3.connect("D:\\GG\\git\\asterpy\\aster_dados.db", uri=True)
    rows = db.execute("SELECT * FROM aster_data").fetchall()

    if type:
        if type not in ['phyll', 'npv', 'qtz']:
            raise ValueError(f"======== The type {type} it is not valid. The value must be 'phyll', 'npv' or 'qtz' ========")

        # Sets index with the index number of the column in the database
        if type == 'phyll':
            index = 5
        elif type == 'npv':
            index = 6
        elif type == 'qtz':
            index = 7
    else:
        return print("======== Please inform the index type ========")

    if period:
        if period not in ['dia', 'noite']:
            raise ValueError(f"======== The value {period} it is not valid. The value must be 'dia' or 'noite' ========")

    if months:
        if months not in ['chuvoso', 'seco']:
            raise ValueError(f"======== The value {months} it is not valid. The value must be 'chuvoso' or 'seco' ========")

        if months == 'chuvoso':
            months = [3, 4, 5, 6, 7, 8, 9] # Mar - Set
        elif months == 'seco':
            months = [10, 11, 12, 1, 2] # Oct - Feb

    min_values: List[float] = []
    max_values: List[float] = []
    # Calculates the minimum value from the database
    for row in rows:
        if row[index]:
            img_period = row[4]
            img_month = int(row[1].split('_')[2][3: 4 + 1])

            if period and img_period != period:
                continue

            if months and img_month not in months:
                continue

            min_values.append(float(row[index].split(':')[0]))
            max_values.append(float(row[index].split(':')[1]))

    mean_min = statistics.mean(min_values)
    mean_max = statistics.mean(max_values)

    median_min = statistics.median(min_values)
    median_max = statistics.median(max_values)

    min = median_min
    max = median_max
    return min, max

def get_period(filename: str=None):
    if not filename:
        raise ValueError(f"Please, inform a valid image")

    hour = int(filename.split('_')[2][11:13])
    if hour >= 6 and hour < 18:
        return 'dia'
    else:
        return 'noite'

def get_months(filename: str=None):
    """
    
    returns 'chuvoso' (3, 4, 5, 6, 7, 8, 9) ou 'seco' (1, 2, 10, 11, 12)"""
    if not filename:
        raise ValueError(f"Please, inform a valid image")

    month = int(filename.split('_')[2][3:4 + 1])
    if month in [3, 4, 5, 6, 7, 8, 9]: # mar - sep
        return 'chuvoso'
    else:
        return 'seco'


def auto_process():
    print(f"Phyll dia chuvoso: {get_min_max('phyll', 'dia', 'chuvoso')}")
    print(f"Phyll dia seco: {get_min_max('phyll', 'dia', 'seco')}")
    print(f"Phyll noite chuvoso: {get_min_max('phyll', 'noite', 'chuvoso')}")
    print(f"Phyll noite seco: {get_min_max('phyll', 'noite', 'seco')}")
    print('='*50)
    print(f"Npv dia chuvoso: {get_min_max('npv', 'dia', 'chuvoso')}")
    print(f"Npv dia seco: {get_min_max('npv', 'dia', 'seco')}")
    print(f"Npv noite chuvoso: {get_min_max('npv', 'noite', 'chuvoso')}")
    print(f"Npv noite seco: {get_min_max('npv', 'noite', 'seco')}")
    print('='*50)
    print(f"Qtz dia chuvoso: {get_min_max('qtz', 'dia', 'chuvoso')}")
    print(f"Qtz dia seco: {get_min_max('qtz', 'dia', 'seco')}")
    print(f"Qtz noite chuvoso: {get_min_max('qtz', 'noite', 'chuvoso')}")
    print(f"Qtz noite seco: {get_min_max('qtz', 'noite', 'seco')}")

    for i in range(3):

        if i == 0:
            inpath = "02_Indices\\01_Phyll\\"
            type = "phyll"

            #file = open(f'Teste\\Histo_mean_Phyll.txt', 'w')

        if i == 1:
            inpath = "02_Indices\\02_Npv\\"
            type = "npv"

            #file = open(f'Teste\\Histo_mean_Npv.txt', 'w')

        if i == 2:
            inpath = "02_Indices\\03_Qtz\\"
            type = "qtz"
            #file = open(f'Teste\\_Qtz.txt', 'w')

        files = os.listdir(inpath)

        for i in range(len(files)):
            file = files[i]

            hour = int(file.split('_')[2][11:13])
            month = int(file.split('_')[2][3:4 + 1])

            if month in [3, 4, 5, 6, 7, 8, 9]: # mar - sep
                months = 'chuvoso'
            else:
                months = 'seco'

            if hour >= 6 and hour < 18:
                period = 'dia'
            else:
                period = 'noite'

            # Makes the threshold clipping
            min, max = get_min_max(type, period, months)
            subprocess.call(['gdal_translate.exe', '-ot', 'Byte', '-quiet' ,'-scale', str(min), str(max), f"{inpath}\\{file}", f"Teste\\Histo_{file}"])

            #im = Image.open(f"03_Histograma\\0{i + 1}_{type}\\{file}_Histo_{}.tif")
            #im.show()

        """
        img2 = cv2.imread(f"Teste\\{file}processed_{type}.tif")

        # Apllies the median filter
        #img2 = cv2.medianBlur(img2, 3)

        cv2.namedWindow(file + "_Processed", cv2.WINDOW_NORMAL)

        cv2.imshow(file + "_Processed", img2)

        # Tries to open the image manually processed
        try:

        except FileExistsError:
            pass


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
        """

def compare(file: str=None, type: str=None):
    if not type:
        return print(f"=== Please inform a type ===")

    if not file:
        return print(f"=== Please inform a file ===")

    # Check if the file is already unziped
    if file not in os.listdir("00_Arquivos"): # Verifica se o arquivo zip já foi extraido
        shutil.unpack_archive(f"00_Arquivos\\{file}.zip", f"00_Arquivos\\{file}")
        print(f"file unpacked")

    out_folder = f"Teste\\{file}_{type}\\"
    try:
        os.mkdir(f"Teste\\{file}_{type}\\")
        os.mkdir(out_folder)
    except FileExistsError:
        pass

    if type == 'phyll':
        dir = '01_Phyll'

    if type == 'npv':
        dir = '02_Npv'

    if type == 'qtz':
        dir = '03_Qtz'

    # 02_Indices\01_Phyll\AST_L1B_00301022014012358_20200213112936_20968_Phyll.tif
    layer_dir = f"01_Layer_Stacking\\{file}_Layer_Stacking.tif"
    index_dir = f"02_Indices\\{dir}\\{file}_{type.capitalize()}.tif"

    # Checks if there is index image
    if not os.path.isfile(index_dir):
        if not os.path.isfile(layer_dir):
            #make layer stack image
            print(f"***********************")
            print(f"Fazendo Layer Stack para {file}")
            ap.layer_stack(file, '')
        # makes index image
        print(f"Fazendo Índice")
        ap.index_calc(file, '')

    period = get_period(file)
    months = get_months(file)

    # Makes the threshold clipping using only period
    min, max = get_min_max(type, period)
    subprocess.call(['gdal_translate.exe', '-ot', 'Byte', '-quiet' ,'-scale', str(min), str(max), index_dir, f"{out_folder}\\{file}_{type}_Period.tif"])
    print(f"1 - min: {min} max: {max}")
    # Makes the threshold clipping using period and months
    min, max = get_min_max(type, period, months)
    subprocess.call(['gdal_translate.exe', '-ot', 'Byte', '-quiet' ,'-scale', str(min), str(max), index_dir, f"{out_folder}\\{file}_{type}_Periodo_e_Meses.tif"])
    print(f"2 - min: {min} max: {max}")

#compare("AST_L1B_00308132009131803_20200213112625_13869", "phyll")
auto_process()