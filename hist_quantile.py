import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import os

def plot_hist(array):
    fig, ax = plt.subplots(figsize=(8,3))

    n, bins, patches = ax.hist(arr, bins=256, ec='black', fc='none', histtype='step')

    plt.show()

dir = "D:\\GG\\git\\asterpy\\02_Indices\\01_Phyll\\"

imgs = os.listdir(dir)


for i in range(5):
    index_img = dir + imgs[1]

    # Open the image
    im = Image.open(index_img)

    # Reads the image as an array
    arr = np.array(im.getdata())

    # Removes the zeros of the array and sorts the array
    arr_nonzero = np.sort(np.ma.masked_equal(arr, 0))

    # Gets the minimun value for threshold
    min = np.nanquantile(arr_nonzero, q=0.75)

    # Gets the maximum value for threshold
    max = np.nanmax(np.ma.masked_invalid(arr_nonzero))

    # Retira os dados invalidos (nan e inf) para obter os valores minimos e maximos
    #arr = np.ma.masked_invalid(arr)


    # Makes the layer stack