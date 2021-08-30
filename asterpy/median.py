import os
import cv2 as cv2
import rasterio

def median_filter(file, path):
    phyll_dir = '01_Phyll\\'
    npv_dir = '02_Npv\\'
    qtz_dir = '03_Qtz\\'

    files_dir = path + '00_Arquivos\\'
    histo_dir = path + '03_Histograma\\'
    median_dir = path + '04_Mediana\\'

    if os.path.isfile(files_dir + file + '\\' + file + '.VNIR_Swath.ImageData2.tif') == True:
        os.remove(histo_dir + 'Merge\\' + file + '_merge.tif')

    print('Processando Mediana...')

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

        # Abre a imagem com o opencv em modo escala de cinza
        img = cv2.imread(histo_dir + dir + file + '_Histo' + index, 0)
        img_median = cv2.medianBlur(img, 3)

        cv2.imwrite(median_dir + dir + file + '_Mediana_no_meta' + index, img_median)

        del img
        del img_median

        # Abre o arquivo do histograma para obter os metadados
        ds0 = rasterio.open(histo_dir + dir + file + '_Histo' + index)

        # Adquire os metadados da imagem
        ras_meta = ds0.profile

        # Abre imagem da mediana sem metadados para ler o array
        ds1 = rasterio.open(median_dir + dir + file + '_Mediana_no_meta' + index)

        # Armazena o array da imagem com filtro mediana
        array = ds1.read(1)

        # Salva imagem com filtro mediana incluindo os metadados da imagem original
        with rasterio.open(median_dir + dir + file + '_Mediana' + index, 'w', **ras_meta) as dts:
            dts.write_band(1, array)

        ds0.close()
        ds1.close()
        del array
        os.remove(median_dir + dir + file + '_Mediana_no_meta' + index)