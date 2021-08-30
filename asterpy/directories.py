import os

def directory_maker(path):
    phyll_dir = '01_Phyll\\'
    npv_dir = '02_Npv\\'
    qtz_dir = '03_Qtz\\'

    files_dir = path + '00_Arquivos\\'
    layer_dir = path + '01_Layer_Stacking\\'
    index_dir = path + '02_Indices\\'
    index_dir_fig = path + '02_Indices\\Figuras\\'
    histo_dir = path + '03_Histograma\\'
    median_dir = path + '04_Mediana\\'
    rgb_dir = path + '05_RGB\\'
    triplete_dir = path + '06_Triplete\\'
    histogram_image_dir = path + '07_Fotos_histograma\\'
    shape_dir = path + '08_Shapes'


    try:
        os.makedirs(files_dir)
        print("Directory" , files_dir,  " Created")
    except FileExistsError:
        pass

    try:
        os.makedirs(layer_dir)
        print("Directory" , layer_dir ,  "Created")
    except FileExistsError:
        pass

    try:
        os.makedirs(index_dir)
        print("Directory" , index_dir ,  "Created")
    except FileExistsError:
        pass

    try:
        os.makedirs(index_dir + phyll_dir)
    except FileExistsError:
        pass

    try:
        os.makedirs(index_dir + npv_dir)
    except FileExistsError:
        pass

    try:
        os.makedirs(index_dir + qtz_dir)
    except FileExistsError:
        pass

    try:
        os.makedirs(index_dir_fig)
        print("Directory", index_dir_fig, "Created")

    except FileExistsError:
        pass

    try:
        os.makedirs(index_dir_fig + phyll_dir)
    except FileExistsError:
        pass

    try:
        os.makedirs(index_dir_fig + npv_dir)
    except FileExistsError:
        pass

    try:
        os.makedirs(index_dir_fig + qtz_dir)
    except FileExistsError:
        pass

    try:
        os.makedirs(histo_dir)
        print("Directory", histo_dir, "Created")
    except FileExistsError:
        pass

    try:
        os.makedirs(histo_dir + phyll_dir)
    except FileExistsError:
        pass

    try:
        os.makedirs(histo_dir + npv_dir)
    except FileExistsError:
        pass

    try:
        os.makedirs(histo_dir + qtz_dir)
    except FileExistsError:
        pass

    try:
        os.makedirs(histo_dir + 'Merge\\')
        print("Directory", histo_dir + 'Merge\\',  "Created")
    except FileExistsError:
        pass

    try:
        os.makedirs(median_dir)
        print("Directory", median_dir, "Created")
    except FileExistsError:
        pass

    try:
        os.makedirs(median_dir + phyll_dir)
    except FileExistsError:
        pass

    try:
        os.makedirs(median_dir + npv_dir)
    except FileExistsError:
        pass

    try:
        os.makedirs(median_dir + qtz_dir)
    except FileExistsError:
        pass

    try:
        os.makedirs(rgb_dir)
        print("Directory", rgb_dir, "Created")
    except FileExistsError:
        pass

    try:
        os.makedirs(rgb_dir + phyll_dir)
    except FileExistsError:
        pass

    try:
        os.makedirs(rgb_dir + npv_dir)
    except FileExistsError:
        pass

    try:
        os.makedirs(rgb_dir + qtz_dir)
    except FileExistsError:
        pass

    try:
        os.makedirs(triplete_dir)
        print("Directory", triplete_dir, "Created")
    except FileExistsError:
        pass

    try:
        os.makedirs(histogram_image_dir)
        print("Directory", histogram_image_dir, "Created")
    except FileExistsError:
        pass

    try:
        os.makedirs(histogram_image_dir + phyll_dir)
    except FileExistsError:
        pass

    try:
        os.makedirs(histogram_image_dir + npv_dir)
    except FileExistsError:
        pass

    try:
        os.makedirs(histogram_image_dir + qtz_dir)
    except FileExistsError:
        pass

    try:
        os.makedirs(shape_dir)
        print("Directory", shape_dir, "Created")
    except FileExistsError:
        pass