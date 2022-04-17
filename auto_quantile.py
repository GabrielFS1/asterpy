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



for i in range(3):

    percentage = 10

    if i == 0:
        inpath = "02_Indices\\01_Phyll\\"
        file = open(f'Teste\\{percentage}%_Phyll.txt', 'w')

    if i == 1:
        inpath = "02_Indices\\02_Npv\\"
        file = open(f'Teste\\{percentage}%_Npv.txt', 'w')

    if i == 2:
        inpath = "02_Indices\\03_Qtz\\"
        file = open(f'Teste\\{percentage}%_Qtz.txt', 'w')


    imgs = os.listdir(inpath)

    for i in range(15):
        img = imgs[i]
        # Open the image
        im = Image.open(inpath + img)

        # Reads the image as an array
        arr = np.array(im.getdata())

        # Removes the zeros of the array and sorts the array
        arr_nonzero = np.sort(np.ma.masked_equal(arr, 0))


        print(f"calculating for {1 - percentage/100}")
        # Gets the minimun value for threshold
        min = np.nanquantile(arr_nonzero, q=(1 - percentage/100))

        # Gets the maximum value for threshold
        max = np.nanmax(np.ma.masked_invalid(arr_nonzero))

        subprocess.call(['gdal_translate.exe', '-ot', 'Byte', '-quiet', '-scale',
                        str(min), str(max), inpath + img, f"Teste\\{percentage}%_Histo_{img}"])

        #img = cv2.imread(f"Teste\\05%_Histo_{img}", 0)

        #img_median = cv2.medianBlur(img, 3)

        file.write(f"{percentage}% - {imgs[i]} - {min} : {max}\n")

        #cv2.imshow('image', img)

        #cv2.waitKey()