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


inpath = "02_Indices\\01_Phyll\\"

imgs = os.listdir(inpath)

img = imgs[4]
# Open the image
im = Image.open(inpath + img)

# Reads the image as an array
arr = np.array(im.getdata())

# Removes the zeros of the array and sorts the array
arr_nonzero = np.sort(np.ma.masked_equal(arr, 0))

# Gets the minimun value for threshold
min = np.nanquantile(arr_nonzero, q=0.75)

# Gets the maximum value for threshold
max = np.nanmax(np.ma.masked_invalid(arr_nonzero))

subprocess.call(['gdal_translate.exe', '-ot', 'Byte', '-quiet', '-scale',
                str(min), str(max), inpath + img, f"Teste\\Histo_{img}"])

img = cv2.imread(f"Teste\\Histo_{img}", 0)

img_median = cv2.medianBlur(img, 3)