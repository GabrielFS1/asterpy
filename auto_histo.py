from calendar import month
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




def get_min_max(type: str=None, period: str=None, months: str=None):
    db = sqlite3.connect("aster_dados.db", uri=True)
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

    sum_min = sum_max = qtd = 0

    # Calculates the minimum value from the database
    for row in rows:
        if row[index]:
            img_period = row[4]
            img_month = int(row[1].split('_')[2][3: 4 + 1])

            if period and img_period != period:
                continue

            if months and img_month not in months:
                continue

            sum_min += float(row[index].split(':')[0]) 
            sum_max += float(row[index].split(':')[1]) 
            qtd += 1

    print(round(sum_min / qtd, 3))
    print(round(sum_max / qtd, 3))

    return round(sum_min / qtd, 3), round(sum_max / qtd, 3)

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
            type = "Phyll"

            #file = open(f'Teste\\Histo_mean_Phyll.txt', 'w')

        if i == 1:
            inpath = "02_Indices\\02_Npv\\"
            type = "Npv"

            #file = open(f'Teste\\Histo_mean_Npv.txt', 'w')

        if i == 2:
            inpath = "02_Indices\\03_Qtz\\"
            type = "Qtz"
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
            min, max = get_min_max('phyll', period, months)
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