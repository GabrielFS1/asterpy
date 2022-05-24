import os


def directory_maker():
    """Creates the """

    dirs = [
        {'name': '00_Arquivos', 'sub_folders': False},
        {'name': '01_Layer_Stacking', 'sub_folders': False},
        {'name': '02_Indices', 'sub_folders': True},
        {'name': '02_Indices\\Figuras\\', 'sub_folders': True},
        {'name': '03_Histograma', 'sub_folders': True},
        {'name': '04_Mediana', 'sub_folders': True},
        {'name': '05_RGB', 'sub_folders': True},
        {'name': '06_Triplete', 'sub_folders': True},
        {'name': '07_Fotos_histograma', 'sub_folders': True},
        {'name': '08_Shapes', 'sub_folders': False}
    ]

    sub_dirs = [
        '01_Phyll',
        '02_Npv',
        '03_Qtz'
    ]

    for directory in dirs:
        try:
            os.makedirs(directory['name'])
            print("Directory", directory['name'],  "Created")
        except FileExistsError:
            pass

        if directory['sub_folders']:
            for sub_dir in sub_dirs:
                try:
                    os.makedirs(f"{directory['name']}\\{sub_dir}")
                    print("Directory", f"{directory['name']}\\{sub_dir}",  "Created")
                except FileExistsError:
                    pass