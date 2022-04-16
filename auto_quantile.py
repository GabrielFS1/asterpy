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


inpath = "02_Indices\\03_Qtz\\"

imgs = os.listdir(inpath)

file = open('values.txt', 'a')

for i in range(10):
    img = imgs[i]
    # Open the image
    im = Image.open(inpath + img)

    # Reads the image as an array
    arr = np.array(im.getdata())

    # Removes the zeros of the array and sorts the array
    arr_nonzero = np.sort(np.ma.masked_equal(arr, 0))

    # Gets the minimun value for threshold
    min = np.nanquantile(arr_nonzero, q=0.95)

    # Gets the maximum value for threshold
    max = np.nanmax(np.ma.masked_invalid(arr_nonzero))

    subprocess.call(['gdal_translate.exe', '-ot', 'Byte', '-quiet', '-scale',
                    str(min), str(max), inpath + img, f"Teste\\Histo_5%_{img}"])

    img = cv2.imread(f"Teste\\Histo_{img}", 0)

    img_median = cv2.medianBlur(img, 3)

    file.write(f"5% - {imgs[i]} - {min} : {max}\n")

    #cv2.imshow('image', img)

    #cv2.waitKey()