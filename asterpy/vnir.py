from asterpy import histogram
import subprocess
import rasterio
from osgeo import gdal
import os

def merge_bands_vnir(file, path, resolution_merge):
    files_dir = path + '00_Arquivos\\'
    histo_dir = path + '03_Histograma\\'

    if os.path.isfile(files_dir + file + '\\' + file + '.VNIR_Swath.ImageData2.tif') == True:
        # Band Red
        r_no_rot = files_dir + file + '\\' + file + '.VNIR_Swath.ImageData2.tif'
        r_rot = histo_dir + 'Merge\\r_rot.tif'
        r = histo_dir + 'Merge\\r.tif'

        # Faz rotação da cena e define resolução da imagem gerada
        gdal.Warp(r_rot, r_no_rot, xRes = resolution_merge, yRes = resolution_merge) #, xRes=90, yRes=90
        # Pega valores para o recorte linear 2%
        min, max = histogram.get_histogram_range(r_rot)
        # Altera escala da imagem com base no intervalo mínimo e máximo
        subprocess.call(['gdal_translate.exe', '-quiet', '-ot', 'Byte', '-scale', str(min), str(max), '0', '255', r_rot, r])
        # Limpa variáveis
        os.remove(r_rot)
        r_no_rot = r_rot = None

        # Band Green
        g_no_rot = files_dir + file + '\\' + file + '.VNIR_Swath.ImageData3N.tif'
        g_rot =  histo_dir + 'Merge\\g_rot.tif'
        g = histo_dir + 'Merge\\g.tif'

        # Faz rotação da cena e define resolução da imagem gerada
        gdal.Warp(g_rot, g_no_rot, xRes = resolution_merge, yRes = resolution_merge)
        # Pega valores para o recorte linear 2% 
        min, max = histogram.get_histogram_range(g_rot)
        # Altera escala da imagem com base no intervalo mínimo e máximo
        subprocess.call(['gdal_translate.exe', '-quiet', '-ot', 'Byte', '-scale', str(min), str(max), '0', '255', g_rot, g])
        # Limpa variáveis
        os.remove(g_rot)
        g_no_rot = g_rot = None

        # Band Blue
        b_no_rot = files_dir + file + '\\' + file + '.VNIR_Swath.ImageData1.tif'
        b_rot = histo_dir + 'Merge\\b_rot.tif'
        b = histo_dir + 'Merge\\b.tif'

        # Faz rotação da cena e define resolução da imagem gerada
        gdal.Warp(b_rot, b_no_rot, xRes = resolution_merge, yRes = resolution_merge)
        # Pega valores para o recorte linear 2%
        min, max = histogram.get_histogram_range(b_rot)
        # Altera escala da imagem com base no intervalo mínimo e máximo
        subprocess.call(['gdal_translate.exe', '-quiet','-ot', 'Byte', '-scale', str(min), str(max), '0', '255', b_rot, b])
        # Limpa variáveis
        os.remove(b_rot)
        b_no_rot = b_rot = None
        
        list_rgb = [r, g, b]

        band_list = list_rgb

        # Pega os metadados do primeiro arquivo
        with rasterio.open(band_list[0]) as src0:
            meta = src0.meta

        # Atualiza número de camadas e o tipo dos dados
        meta.update(count = len(band_list), interleave = 'band', compress = 'lzw')

        # Junta as camadas do arquivo e escreve em uma única imagem
        with rasterio.open(histo_dir + 'Merge\\' + file + '_merge.tif', 'w', **meta) as dst:
            for id, layer in enumerate(band_list, start = 1):
                with rasterio.open(layer) as src1:
                    dst.write_band(id, src1.read(1))

        r = g = b = list_rgb = meta = None

        # Cria janela para visualização de imagens
        os.remove(histo_dir + 'Merge\\' + "r.tif")
        os.remove(histo_dir + 'Merge\\' + "g.tif")
        os.remove(histo_dir + 'Merge\\' + "b.tif")
        
        return 0