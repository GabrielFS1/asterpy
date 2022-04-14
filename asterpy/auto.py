import subprocess
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from asterpy.stack import layer_stack
from asterpy.indice import index_calc

def auto_threshold(inpath, filename, output, index: str=None):

    if index not in ['phyll', 'npv', 'qtz']:
        raise ValueError("The index it is not valid. Must be 'phyll', 'npv' or 'qtz'")

    # Open the image
    im = Image.open(inpath)

    # Reads the image as an array
    arr = np.array(im.getdata())

    # Removes the zeros of the array and sorts the array
    arr_nonzero = np.sort(np.ma.masked_equal(arr, 0))

    # Gets the minimun value for threshold
    min = np.nanquantile(arr_nonzero, q=0.75)

    # Gets the maximum value for threshold
    max = np.nanmax(np.ma.masked_invalid(arr_nonzero))

    subprocess.call(['gdal_translate.exe', '-ot', 'Byte', '-quiet', '-scale',
                    str(min), str(max), inpath, f"{output}\\{filename}_Histo_{index.capitalize()}"])

    return min, max