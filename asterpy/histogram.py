from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

# Cria figura jpg com o histograma recortado
def histogram_image_save(file, path, index, dir, min, max):
    index_dir = path + '02_Indices\\'
    fotos_dir = path + '07_Fotos_histograma\\'

    img_in = index_dir + dir + file + index
    im = Image.open(index_dir + dir + file + index)

    # Cria o array da imagem
    Z = np.array(im.getdata())

    # Retira os dados invalidos (nan e inf) para obter os valores minimos e maximos
    Z = np.ma.masked_invalid(Z)

    #Z = (Z[np.where(Z != 0)])
    max_thres = np.ma.masked_invalid(Z).max()

    fig, (ax, ax1) = plt.subplots(ncols=2, figsize=(8,3))
    n,bins,patches = ax.hist(Z, bins=256, ec='white', fc='none', histtype='step')
    ax.set_xlim(0,max_thres)
    ax1.set_xlim(0,255)

    # Visual do histograma de entrada (similar ao ENVI)
    ax.spines['bottom'].set_color('white')
    ax.spines['top'].set_color('white')
    ax.spines['right'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.xaxis.label.set_color('white')
    fig.patch.set_facecolor('black')
    ax.patch.set_facecolor('black')
    ax.title.set_color('white')
    ax.axes.get_yaxis().set_visible(False)

    # Visual do histograma de saída (similar ao ENVI)
    ax1.spines['bottom'].set_color('white')
    ax1.spines['top'].set_color('white')
    ax1.spines['right'].set_color('white')
    ax1.spines['left'].set_color('white')
    ax1.tick_params(axis='x', colors='white')
    ax1.tick_params(axis='y', colors='white')
    ax1.xaxis.label.set_color('white')
    fig.patch.set_facecolor('black')
    ax1.patch.set_facecolor('black')
    ax1.title.set_color('white')
    ax1.axes.get_yaxis().set_visible(False)

    # Converte os valores do histrograma para uint8 (BYTE)
    def normalize8(I, min_float, max_float):
        mn_float = min

        mx_float = max

        mx_float -= mn_float

        I = ((I - mn_float)/mx_float) * 255
        return I.astype(np.uint8)

    #txt = ax.text(5, 30, f'{min_thres} : {max_thres}', fontsize=12)
    axvline1 = ax.axvline(min, color='white', linestyle='--', lw=1, label="min")
    axvline2 = ax.axvline(max, color='white', linestyle='--', lw=1, label="max")

    # Define o título dos dois hitogramas
    ax.set_title(f'{min} : {max}\n\nInput Histogram', fontsize=10)
    ax1.set_title('Output Histogram', fontsize=8)

    # Cria histograma de saída com valores normalizados em uint8
    n, bins, patches = ax1.hist(normalize8(Z, min, max), bins=256, ec='red', fc='none', histtype='step')

    # Cria subtítulo com o nome do arquivo recortado
    fig.suptitle(file + ' ' + index.split('.')[0][1:], color='white', fontsize=11)

    plt.tight_layout()

    # Salva a figura
    plt.savefig(fotos_dir + dir + file + '_Histo' + index.split('.')[0] + '.jpg')

def get_histogram_range(img_path):
    # Abre a imagem
    im= Image.open(img_path)

    # Cria o array da imagem
    Z = np.array(im.getdata())

    im = None

    Z = np.ma.masked_invalid(Z)

    if '_Phyll' in img_path or '_Npv' in img_path or '_Qtz' in img_path:
        bins_list = 256
        arg = False
    else:
        # Composição VNIR
        bins_list = []
        for i in range(257):
            arg = True
            bins_list.append(i)

    def get_total(n):
        total = 0
        for num in n:
            total = total + num
        return total

    def get_values(arr, arg):
        if arg == True:
            fig, ax = plt.subplots()
            n,bins,patches = ax.hist(arr, bins=bins_list, density=True)

            total = get_total(n)
            points = 0

            smll_error_min = abs(2 - n[0]/total*100)
            smll_error_max = abs(98 - n[0]/total*100)

            min_value = bins[0]
            max_value = bins[0]

            for i, num in enumerate(n, start=0):
                points = points + num
                error_min = abs(2 - ((points/total*100) - (n[0]/total*100)))
                error_max = abs(98 - points/total*100)

                if error_min < smll_error_min:
                    smll_error_min = error_min
                    min_value = bins[i]

                if error_max < smll_error_max:
                    smll_error_max = error_max
                    max_value = bins[i]
                
                if points/total*100 > 99:
                    plt.close(fig)
                    smll_error_max = smll_error_min = error_min = error_max = bins = total = None
                    return [round(min_value, 3), round(max_value, 3)]
        else:
            fig, ax = plt.subplots()
            n,bins,patches = ax.hist(arr, bins=bins_list, density=True)

            total = get_total(n)
            points = 0

            smll_error_min = abs(2 - n[0]/total*100)
            smll_error_max = abs(98 - n[0]/total*100)

            min_value = bins[0]
            max_value = bins[0]

            for i, num in enumerate(n, start=0):
                points = points + num
                #print(f"n: {round(n[i]*100, 2)}% ; bins: {int(bins[i])}; points: {points} percentage: {round(points/total*100, 2)}")
                error_min = abs(2 - points/total*100)
                error_max = abs(98 - points/total*100)

                if error_min < smll_error_min:
                    smll_error_min = error_min
                    min_value = bins[i]

                if error_max < smll_error_max:
                    smll_error_max = error_max
                    max_value = bins[i]

                if points/total*100 > 99:
                    plt.close(fig)
                    # Limpa vaiáveis    
                    smll_error_max = smll_error_min = error_min = error_max = bins = total = None
                    return [round(min_value, 3), round(max_value, 3)]
    return get_values(Z, arg)