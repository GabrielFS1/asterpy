from inspect import stack
import os
from pathlib import Path
import sys
import os.path
import shutil
from typing import List
import asterpy as ap
import warnings
from asterpy import threshold
import rasterio

from asterpy import layer_stacking, band_calc, database, directories

warnings.filterwarnings("ignore", category=rasterio.errors.NotGeoreferencedWarning)

# Resolução da composição coloridas das bandas VNIR
resolution_merge = 60

# Define o diretório padrão onde as pastas ficarão salvas

# Cria os diretórios se não existir 
directories.directory_maker()

# Caminhos para os diretórios que contém os três índices
phyll_dir = '01_Phyll\\'
npv_dir = '02_Npv\\'
qtz_dir = '03_Qtz\\'
path = ''
files_dir = '00_Arquivos\\'
layer_dir = '01_Layer_Stacking\\'
index_dir = '02_Indices\\'

def processing(file):

    if database.check_register(file): # Verifica se o arquivo ja está registrado no banco
        if database.check_final_checker(file): # Não da continuidade se o arquivo já foi finalizado
            return
    else:
        database.new_register(file) # Insere o arquivo no banco de dados

    bands_files: List[Path] = [
        f"00_Arquivos\\{file}\\{file}.TIR_Swath.ImageData10.tif",
        f"00_Arquivos\\{file}\\{file}.TIR_Swath.ImageData11.tif",
        f"00_Arquivos\\{file}\\{file}.TIR_Swath.ImageData12.tif",
        f"00_Arquivos\\{file}\\{file}.TIR_Swath.ImageData13.tif",
        f"00_Arquivos\\{file}\\{file}.TIR_Swath.ImageData14.tif"
    ]
    layer_stack_img = layer_stacking.layer_stack(bands_files, 'Teste\\layer_test.tif')

    phyll_img = band_calc.phyll_calc(layer_stack_img, f"02_Indices\\01_Phyll\\{file}_Phyll.tif")
    npv_img = band_calc.npv_calc(layer_stack_img, f"02_Indices\\02_Npv\\{file}_Npv.tif")
    qtz_img = band_calc.qtz_calc(layer_stack_img, f"02_Indices\\03_Qtz\\{file}_Qtz.tif")

    ## Composição colorida com as bandas 1, 2 e 3
    #ap.merge_bands_vnir(file, path, resolution_merge)

    print("Iniciando o processamento do histograma, após o ajuste, clique com o botão direito do mouse na maior imagem a sua esquerda")
    for i in range(0, 3):
        if i == 0:
            dir = phyll_dir
            index = '_Phyll.tif'
            func = database.insert_phyll

        elif i == 1:
            dir = npv_dir
            index = '_Npv.tif'
            func = database.insert_npv

        elif i == 2:
            dir = qtz_dir
            index = '_Qtz.tif'
            func = database.insert_qtz

        # Gera o histograma ajustável da imagem
        threshold.threshold_adjust_window(file, path, dir, index, func)

    # Filtro de mediana
    ap.median_filter(file)

    # Aplica mascara RGB para a imagem
    ap.color_mapping(file)

    # Mescla as três medianas em um arquivo rgb
    ap.triplete_image(file, path)

    # Gera a figura do index antes do threshold
    ap.generate_index_image(file, path)

    # Atualiza o banco de dados classificando cena como finalizada
    ap.image_complete(file)

    print(f'\033[32mArquivo {file} finalizado!\033[m')

def extract_zip(file):
    # Verifica se não há uma pasta do arquivo
    print(f'Extraindo arquivo {file}')
    # Extrai arquivo zip
    shutil.unpack_archive(files_dir + file, files_dir + file.split(".")[0]+'\\')

os.system('cls' if os.name == 'nt' else 'clear')
# Requisita entrada do usuário enquanto for digitada uma opção inválida
opt = input('''\033[1m(1) Processar todos os arquivos da pasta 00\033[m\n\033[1;32m(2) Processar uma única imagem\033[0m\n\033[1;34m(3) Fazer shapefile de todas imagens disponíveis\033[0m\n\033[1;31m(0) Sair\033[0m\n\n\033[4mSelecione uma opção.\033[0m\n\033[1m==> \033[0m''')

while opt.isdigit() == False or int(opt) not in range(0,4):
    os.system('cls' if os.name == 'nt' else 'clear')
    opt = input('''\033[1m(1) Processar todos os arquivos da pasta 00\033[m\n\033[1;32m(2) Processar uma única imagem\033[0m\n\033[1;34m(3) Fazer shapefile de todas imagens disponíveis\033[0m\n\033[1;31m(0) Sair\033[0m\n\n\033[4mSelecione uma opção.\033[0m\n\033[1m==> \033[0m''')

# Finaliza a execução do programa
if opt == '0':
    print("\033[32mPrograma Finalizado\033[0m")
    os.system('cls' if os.name == 'nt' else 'clear')
    sys.exit()

elif opt == '1':
    for file in os.listdir(files_dir):
        if len(file.split(".")) == 1 and file.split("_")[0] == 'AST': # Verifica se o arquivo é uma pasta de um arquivo ASTER
            processing(file)
        else:
            if file.split(".")[-1] == 'zip' and file.split("_")[0] == 'AST':
                file = file.split(".")[0]
                if database.check_register(file): # Verifica se o arquivo ja está registrado no banco
                    if database.check_final_checker(file): # Não da continuidade se o arquivo já foi finalizado
                        continue
                else:
                    database.new_register(file) # Insere o arquivo no banco de dados

                if file not in os.listdir(files_dir): # Verifica se o arquivo zip já foi extraido
                    extract_zip(file + '.zip')

                processing(file)

    print("\033[1;32mTodos os arquivos na pasta já foram processados, adicione outros arquivos. Para refazer uma cena utilize a opção 2 do menu.\033[0m\n")

# Processa/Reprocessa um único arquivo por completo
elif opt == '2':
    # Pede para o usuário inserir os últimos digitos no nome da pasta
    num = str(input("\033[1;34mEscreva os últimos digitos do nome do arquivo:\033[0m "))

    file = None

    # Procura por todos os arquivos e compara os últimos digitos de cada um
    for archive in os.listdir(files_dir):
        if archive.split('_')[-1] == num:
            file = archive
            break

    # Fecha o programa caso não encontre o arquivo com os digitos especificados
    if not file:
        print("\033[1;31mArquivo não encontrado\033[0m\n")
        sys.exit()

    if file.split('.')[-1] == 'zip':
        extract_zip(file + '.zip')

    file = file.split('.')[0]
    # Incia o processamento do arquivo
    print(f'\033[1;33mIniciando o processamento do arquivo \033[0m{file}')
    
    # Verifica se o nome da cena já consta no banco de dados
    if  ap.check_register(file) == True:
        processing(file)
    
    else:
        # Insere o documento no banco de dados
        ap.new_register(file)
        # Ínicia o processamento
        processing(file)

    print(f'\033[32mArquivo {file} finalizado!\033[m')

# Gera todos os shapefiles
elif opt == '3':
    for file in os.listdir(files_dir):
        if len(file.split('.')) == 1 and file.split('_')[0] == 'AST':
            # Cria o shapefile
            ap.make_polygon(file, path)
        else:
             # Checa se é arquivo .zip
            if file.split(".")[-1] == 'zip':
                if file.split(".")[0] not in os.listdir(files_dir):
                    extract_zip(file)
                    ap.make_polygon(file.split(".")[0], path)
                # Caso o arquivo .zip já foi descompactado
                else:
                    #print(f'pasta para {file} encontrada')
                    ap.make_polygon(file.split(".")[0], path)