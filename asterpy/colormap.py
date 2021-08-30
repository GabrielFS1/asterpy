import matplotlib.pyplot as plt
import matplotlib
import rasterio
import os
from osgeo import gdal

# Colormap rainbow https://stackoverflow.com/questions/34768717/matplotlib-unable-to-save-image-in-same-resolution-as-original-image
rainbow = {'red': ((0.0, 0.0, 0.0),
                (0.1, 0.5, 0.5),
                (0.2, 0.0, 0.0),
                (0.4, 0.2, 0.2),
                (0.6, 0.0, 0.0),
                (0.8, 1.0, 1.0),
                (1.0, 1.0, 1.0)),
        'green':((0.0, 0.0, 0.0),
                (0.1, 0.0, 0.0),
                (0.2, 0.0, 0.0),
                (0.4, 1.0, 1.0),
                (0.6, 1.0, 1.0),
                (0.8, 1.0, 1.0),
                (1.0, 0.0, 0.0)),
        'blue': ((0.0, 0.0, 0.0),
                (0.1, 0.5, 0.5),
                (0.2, 1.0, 1.0),
                (0.4, 1.0, 1.0),
                (0.6, 0.0, 0.0),
                (0.8, 0.0, 0.0),
                (1.0, 0.0, 0.0))}

my_cmap = matplotlib.colors.LinearSegmentedColormap('my_colormap',rainbow,256)

def color_mapping(file, path):
    phyll_dir = '01_Phyll\\'
    npv_dir = '02_Npv\\'
    qtz_dir = '03_Qtz\\'

    median_dir = path + '04_Mediana\\'
    rgb_dir = path + '05_RGB\\'

    print("Criando imagem RGB...")
    dpi = 80

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

        im_data = plt.imread(median_dir + dir + file + '_Mediana' + index)
        height, width = im_data.shape

        # Define o tamanho da figura de acordo com o tamanho imagem
        figsize = width / float(dpi), height / float(dpi)

        # Cria a figura no tamanho correto
        fig = plt.figure(figsize=figsize)
        ax = fig.add_axes([0, 0, 1, 1])

        # Esconde as informações dos eixos
        ax.axis('off')

        # Aplica o color mapping a imagem
        im = ax.imshow(im_data, interpolation='nearest', aspect='auto', cmap=my_cmap) 

        # Salva a imagem
        fig.savefig(rgb_dir + dir + file + '_RGBA' + index, dpi=dpi)

        # Obtém os metadados da imagem original
        dataset_orginal = rasterio.open(median_dir + dir + file + '_Mediana' + index)
        ras_meta = dataset_orginal.profile

        # Define o numero de bandas como 4
        ras_meta['count'] = 4

        # Abre a image RGB sem metadados para ler as bandas
        dataset_rgb = gdal.Open(rgb_dir + dir + file + '_RGBA' + index)

        r = dataset_rgb.GetRasterBand(1).ReadAsArray()
        g = dataset_rgb.GetRasterBand(2).ReadAsArray()
        b = dataset_rgb.GetRasterBand(3).ReadAsArray()

        sum_rgb = r + g + b

        # Verifica a partir da soma das três bandas, se houver qualquer dados em qualquer banda, define como 255 (opaco)
        sum_rgb[sum_rgb>0] = 255

        descriptions = [
        'Band Red',
        'Band Green',
        'Band Blue',
        'Band Alpha']

        # Insere as bandas em uma imagem com os metadados
        with rasterio.open(rgb_dir + dir + file + '_RGB' + index, 'w', **ras_meta) as dst0:
            for i in range (1,4):
                dst0.write_band(i, dataset_rgb.GetRasterBand(i).ReadAsArray())
                dst0.set_band_description(i, descriptions[i-1])
            # Banda alpha que define transparência
            dst0.write_band(4, sum_rgb)
            dst0.set_band_description(4, descriptions[3])

        # Limpa variáveis e remove arquivos sem uso
        dataset_orginal.close()
        dataset_rgb = None
        os.remove(rgb_dir + dir + file + '_RGBA' + index)

        plt.close('all')
