import os
import sys
import os.path
import shutil
import asterpy as ap

# Resolução da composição coloridas das bandas VNIR
resolution_merge = 60

# Define o diretório padrão onde as pastas ficarão salvas
path = ''

# Cria os diretórios se não existir 
ap.directory_maker(path)

# Caminhos para os diretórios que contém os três índices
phyll_dir = '01_Phyll\\'
npv_dir = '02_Npv\\'
qtz_dir = '03_Qtz\\'

files_dir = path + '00_Arquivos\\'
layer_dir = path + '01_Layer_Stacking\\'
index_dir = path + '02_Indices\\'

def processing(file):

    if ap.check_register(file): # Verifica se o arquivo ja está registrado no banco
        if ap.check_final_checker(file): # Não da continuidade se o arquivo já foi finalizado
            return
    else:
        ap.new_register(file) # Insere o arquivo no banco de dados

    print(f'\033[1;33mIniciando o processamento do arquivo\033[0m {file}')

    if os.path.isfile(layer_dir + file + '_Layer_Stacking.tif') == False:
        ap.layer_stack(file, path)

    if os.path.isfile(index_dir + phyll_dir + file + '_Phyll.tif') == False or  os.path.isfile(index_dir + npv_dir + file + '_Npv.tif') == False or os.path.isfile(index_dir + qtz_dir + file + '_Qtz.tif') == False:
        ap.index_calc(file, path)

    # Composição colorida com as bandas 1, 2 e 3
    ap.merge_bands_vnir(file, path, resolution_merge)

    print("Iniciando o processamento do histograma, após o ajuste, clique com o botão direito do mouse na maior imagem a sua esquerda")
    for i in range(0, 3):
        if i == 0:
            dir = phyll_dir
            index = '_Phyll.tif'
            func = ap.insert_phyll

        elif i == 1:
            dir = npv_dir
            index = '_Npv.tif'
            func = ap.insert_npv

        elif i == 2:
            dir = qtz_dir
            index = '_Qtz.tif'
            func = ap.insert_qtz

        # Gera o histograma ajustável da imagem
        ap.threshold_adjust_window(file, path, dir, index, func)

    # Filtro de mediana
    ap.median_filter(file, path)

    # Aplica mascara RGB para a imagem
    ap.color_mapping(file, path)

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
                if ap.check_register(file): # Verifica se o arquivo ja está registrado no banco
                    if ap.check_final_checker(file): # Não da continuidade se o arquivo já foi finalizado
                        continue
                else:
                    ap.new_register(file) # Insere o arquivo no banco de dados

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