import rasterio

def triplete_image(file, path):
    phyll_dir = '01_Phyll\\'
    npv_dir = '02_Npv\\'
    qtz_dir = '03_Qtz\\'

    merge_rgb_dir = path + '06_Triplete\\'

    median_dir = path + '04_Mediana\\'

    print('Criando Triplete...')
    
    r = median_dir + qtz_dir + file + '_Mediana_Qtz.tif'
    g = median_dir + npv_dir + file + '_Mediana_Npv.tif'
    b = median_dir + phyll_dir + file + '_Mediana_Phyll.tif'

    r_arr = rasterio.open(r).read(1)
    g_arr = rasterio.open(g).read(1)
    b_arr = rasterio.open(b).read(1)

    list_rgb = [r, g, b]

    # Soma cada pixels das três bandas
    sum_rgb = r_arr + g_arr + b_arr

    # Se a soma do pixel é maior que zero, atribui o valor 255
    sum_rgb[sum_rgb>0] = 255

    descriptions = [
    'Band Red',
    'Band Green',
    'Band Blue',
    'Band Alpha']

    # Le os metadados do primeiro arquivo
    with rasterio.open(list_rgb[0]) as src0:
        meta = src0.meta

    # Atualiza numero de camadas e o tipo dos dados
    meta.update(count = 4, interleave = 'band', compress = 'lzw')

    # Le cada camada do arquivo e escreve em um arquivo único
    with rasterio.open(merge_rgb_dir + file + '_Triplete.tif', 'w', **meta) as dts:
        for id, layer in enumerate(list_rgb, start=1):
            with rasterio.open(layer) as src1:
                dts.write_band(id, src1.read(1))
                dts.set_band_description(id, descriptions[id-1])
        dts.write_band(4, sum_rgb)
        dts.set_band_description(4, descriptions[3])

    list_rgb = descriptions = meta = r_arr = g_arr = b_arr = None