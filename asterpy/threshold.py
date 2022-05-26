from pathlib import Path
from typing import Union
import asterpy as ap
import cv2 as cv2
from PIL import Image
import matplotlib.pyplot as plt
import subprocess
import rasterio
import matplotlib
import sys
import os
import numpy as np

from asterpy import histogram

def thredhold_image(infile: Union[str, Path], outpath: Union[str, Path], min: float, max: float):
    subprocess.call(['gdal_translate.exe', '-ot', 'Byte', '-quiet', '-scale', str(min), str(max), infile, outpath])
    return outpath

def threshold_adjust_window(file, path, dir, index, func):
    files_dir = path + '00_Arquivos\\'
    index_dir = path + '02_Indices\\'
    histo_dir = path + '03_Histograma\\'

    window_name = file
    zoom_window = 'zoom'
    dragging = False

    def on_click(event):
        global histo
        if event.xdata == None:
            return
        # Pega os valores atuais das linhas
        frst_cx = axvline1.get_xdata()
        scnd_cx = axvline2.get_xdata()
        # Confere se os valores estão armazenados em uma lista
        if isinstance(frst_cx, list):
            frst_cx = round(float(frst_cx[0]), 3)
        if isinstance(scnd_cx, list):
            scnd_cx = round(float(scnd_cx[0]), 3)

        xdata = float(event.xdata)

        line_range = max_thres/255

        # Confere se o usuário clicou na primeira linha
        if xdata < (frst_cx + line_range) and xdata > (frst_cx - line_range):
            start_drag('axvline1')

        # Confere se o usuário clicou na segunda linha
        elif xdata < (scnd_cx + line_range) and xdata > (scnd_cx - line_range):
            start_drag('axvline2')
        else:
            return

    def start_drag(line):
        global drag_line
        # Guarda a linha selecionada
        drag_line = line

        # Detecta movimentação do mouse
        fig.canvas.mpl_connect('motion_notify_event', drag_update)
        # Detecta quando o mouse é solto
        fig.canvas.mpl_connect('button_release_event', end_drag)

    def drag_update(event):
        global drag_line, xdata

        if event.xdata == None:
            return

        xdata = float(event.xdata)

        frst_cx = axvline1.get_xdata()
        scnd_cx = axvline2.get_xdata()

        # Confere se os valores estão armazenados em uma lista
        if isinstance(frst_cx, list):
            frst_cx = round(float(frst_cx[0]), 3)
        if isinstance(scnd_cx, list):
            scnd_cx = round(float(scnd_cx[0]), 3)

        # Move a primeira linha
        if drag_line == 'axvline1':
            if xdata <= scnd_cx - max_thres/255:
                axvline1.set_xdata(xdata)
                ax.set_title(
                    f'{round(xdata, 3)} : {round(scnd_cx, 3)}', fontsize=12)
                fig.canvas.draw_idle()

            else:
                axvline1.set_xdata(scnd_cx - max_thres/255)
                ax.set_title(
                    f'{round(scnd_cx - max_thres/255, 3)} : {round(scnd_cx, 3)}', fontsize=12)
                fig.canvas.draw_idle()
        # Move a segunda linha
        elif drag_line == 'axvline2':
            if xdata >= frst_cx + max_thres/255:
                axvline2.set_xdata(xdata)
                ax.set_title(
                    f'{round(frst_cx, 3)} : {round(xdata, 3)}', fontsize=12)
                fig.canvas.draw_idle()
            else:
                axvline2.set_xdata(frst_cx + max_thres/255)
                ax.set_title(
                    f'{round(frst_cx, 3)} : {round(frst_cx + max_thres/255, 3)}', fontsize=12)
                fig.canvas.draw_idle()

    # Quando soltar o botão do mouse
    def end_drag(event):
        global arr, x_zoom, y_zoom, arr_thres
        fig.canvas.mpl_disconnect(fig.canvas.mpl_connect(
            'motion_notify_event', drag_update))
        fig.canvas.mpl_disconnect(fig.canvas.mpl_connect(
            'button_release_event', end_drag))

        histo_min = axvline1.get_xdata()
        histo_max = axvline2.get_xdata()

        if isinstance(histo_min, list):
            histo_min = round(float(histo_min[0]), 3)
        if isinstance(histo_max, list):
            histo_max = round(float(histo_max[0]), 3)

        ax.set_title(
            f'{round(histo_min, 3)} : {round(histo_max, 3)}', fontsize=12)

        subprocess.call(['gdal_translate.exe', '-ot', 'Byte', '-quiet', '-scale', str(
            histo_min), str(histo_max), img_in, histo_dir + dir + file + '_Histo' + index])
        arr_thres = cv2.imread(histo_dir + dir + file + '_Histo' + index)

        cv2.imshow(window_name, arr_thres)
        try:
            crop_image_index(x_zoom, y_zoom)
        except:
            crop_image_index(200, 200)

    def crop_image_index(x, y):
        try:
            cropped = arr_thres[y-size_thres_y:y +
                                size_thres_y, x-size_thres_x:x+size_thres_x]
            resized_cropped = cv2.resize(cropped, (size_thres_x, size_thres_y))
            cv2.imshow(zoom_window, resized_cropped)
        except:
            return

    def crop_image_merge(x, y):
        try:
            merge_cropped = merge[y-size_merge_y:y +
                                  size_merge_y, x-size_merge_x:x+size_merge_x]
            resized_merge_cropped = cv2.resize(
                merge_cropped, (size_merge_x, size_merge_y))
            cv2.imshow(zoom_window_2, resized_merge_cropped)
        except:
            return

    size_merge_y = None
    size_merge_x = None
    merge_array = None

    dragging_merge = False

    def zoom_index(x, y):
        global x_zoom, y_zoom
        x_tresh = size_thres_x
        y_tresh = size_thres_y

        if y > y_tresh and x > x_tresh and y < index_array.shape[0] - y_tresh and x < index_array.shape[1] - x_tresh:
            crop_image_index(x, y)
        elif y < y_tresh and x < x_tresh:
            return
        elif y < y_tresh and x > index_array.shape[1] - x_tresh:
            return
        elif y < y_tresh:
            y = y_tresh
            crop_image_index(x, y)
        elif x < x_tresh and y > index_array.shape[0] - y_tresh:
            return
        elif x < x_tresh:
            x = x_tresh
            crop_image_index(x, y)
        elif x > index_array.shape[1] - x_tresh and y > index_array.shape[0] - y_tresh:
            return
        elif x > index_array.shape[1] - x_tresh:
            x = index_array.shape[1] - x_tresh
            crop_image_index(x, y)
        elif y > index_array.shape[0] - y_tresh:
            y = index_array.shape[0] - y_tresh
            crop_image_index(x, y)
        x_zoom = x
        y_zoom = y

    def zoom_merge(x, y):
        if y > size_merge_y and x > size_merge_x and y < merge_array.shape[0] - size_merge_y and x < merge_array.shape[1] - size_merge_x:
            crop_image_merge(x, y)
        elif y < size_merge_y and x < size_merge_x:
            return
        elif y < size_merge_y:
            y = size_merge_y
            crop_image_merge(x, y)
        elif x < size_merge_x:
            x = size_merge_x
            crop_image_merge(x, y)
        elif x > merge_array.shape[1] - size_merge_x and y > merge_array.shape[0] - size_merge_y:
            return
        elif x > merge_array.shape[1] - size_merge_x:
            x = merge_array.shape[1] - size_merge_x
            crop_image_merge(x, y)
        elif y > merge_array.shape[0] - size_merge_y:
            y = merge_array.shape[0] - size_merge_y
            crop_image_merge(x, y)

    def CallBackFunc_index(event, x, y, flags, param):
        global dragging
        if event == cv2.EVENT_RBUTTONDOWN:
            fig.canvas.mpl_disconnect(
                fig.canvas.mpl_connect('button_press_event', on_click))
            fig.canvas.mpl_disconnect(fig.canvas.mpl_connect(
                'motion_notify_event', drag_update))
            fig.canvas.mpl_disconnect(fig.canvas.mpl_connect(
                'button_release_event', end_drag))
            fig.canvas.mpl_disconnect(
                fig.canvas.mpl_connect('close_event', on_close))

            # Gets the values of the two lines in the histogram
            histo_min = axvline1.get_xdata()
            histo_max = axvline2.get_xdata()

            if isinstance(histo_min, list):
                histo_min = round(float(histo_min[0]), 3)
            else:
                histo_min = round(axvline1.get_xdata(), 3)
            if isinstance(histo_max, list):
                histo_max = round(float(histo_max[0]), 3)
            else:
                histo_max = round(axvline2.get_xdata(), 3)

            func(file, f'{str(histo_min)} : {str(histo_max)}')

            ap.histogram_image_save(
                file, path, index, dir, float(histo_min), float(histo_max))

            cv2.destroyAllWindows()

            plt.close('all')

        try:
            if event == cv2.EVENT_LBUTTONDOWN:
                dragging = True

            elif event == cv2.EVENT_LBUTTONUP:
                dragging = False

            if event == cv2.EVENT_MOUSEMOVE:
                if dragging == True:
                    zoom_index(x, y)
                    if os.path.isfile(files_dir + file + '\\' + file + '.VNIR_Swath.ImageData2.tif') == True:
                        x = int(
                            x * merge_array.shape[1] / index_array.shape[1])
                        y = int(
                            y * merge_array.shape[0] / index_array.shape[0])
                        zoom_merge(x, y)
        except:
            return

    def CallBackFunc_merge(event, x, y, flags, param):
        global dragging_merge
        try:
            if event == cv2.EVENT_LBUTTONDOWN:
                dragging_merge = True

            elif event == cv2.EVENT_LBUTTONUP:
                dragging_merge = False

            if event == cv2.EVENT_MOUSEMOVE:
                if dragging_merge == True:
                    zoom_merge(x, y)
                    x = int(x * index_array.shape[1] / merge_array.shape[1])
                    y = int(y * index_array.shape[0] / merge_array.shape[0])
                    zoom_index(x, y)
        except:
            return

    img_in = index_dir + dir + file + index

    dragging = False

    # Abre a imagem
    im = Image.open(img_in)

    # Cria o array da imagem
    Z = np.array(im.getdata())

    # Retira os dados invalidos (nan e inf) para obter os valores minimos e maximos
    Z = np.ma.masked_invalid(Z)

    max_thres = Z.max()

    min, max = histogram.get_histogram_range(img_in)

    ds = rasterio.open(img_in)
    index_array = ds.read(1)
    ds.close()

    subprocess.call(['gdal_translate.exe', '-ot', 'Byte', '-quiet', '-scale',
                    str(min), str(max), img_in, histo_dir + dir + file + '_Histo' + index])

    # Cria janela para visualização de imagens
    arr = cv2.imread(histo_dir + dir + file + '_Histo' + index)

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.namedWindow(zoom_window, cv2.WINDOW_NORMAL)

    cv2.resizeWindow(window_name, 600, 450)
    cv2.resizeWindow(zoom_window, 270, 270)

    cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
    cv2.setWindowProperty(zoom_window, cv2.WND_PROP_TOPMOST, 1)

    cv2.moveWindow(window_name, 10, 10)
    cv2.moveWindow(zoom_window, 5, 460)

    if os.path.isfile(files_dir + file + '\\' + file + '.VNIR_Swath.ImageData2.tif') == True:
        merge = cv2.imread(histo_dir + 'Merge\\' + file + '_merge.tif')

        ds = rasterio.open(histo_dir + 'Merge\\' + file + '_merge.tif')
        merge_array = ds.read(1)
        ds.close()

        window_name_2 = 'Merge'
        zoom_window_2 = 'Zoom'

        cv2.namedWindow(window_name_2, cv2.WINDOW_NORMAL)
        cv2.namedWindow(zoom_window_2, cv2.WINDOW_NORMAL)

        # Redimensionamento das janelas
        cv2.resizeWindow(window_name_2, 400, 350)
        cv2.resizeWindow(zoom_window_2, 400, 350)

        # Janela ajustável
        cv2.setWindowProperty(window_name_2, cv2.WND_PROP_TOPMOST, 1)
        cv2.setWindowProperty(zoom_window_2, cv2.WND_PROP_TOPMOST, 1)

        # Posição das janelas
        cv2.moveWindow(window_name_2, 600, 10)
        cv2.moveWindow(zoom_window_2, 1000, 10)

        percent_merge = 10/100

        size_merge_x = int(merge_array.shape[1] * percent_merge)
        size_merge_y = int(merge_array.shape[0] * percent_merge)

        cv2.setMouseCallback(window_name_2, CallBackFunc_merge)

        cv2.imshow(window_name_2, merge)

    # Porcentagem de zoom
    percent_thres = 10/100

    size_thres_x = int(index_array.shape[1] * percent_thres)
    size_thres_y = int(index_array.shape[0] * percent_thres)

    cv2.setMouseCallback(window_name, CallBackFunc_index)

    cv2.imshow(window_name, arr)

    fig, ax = plt.subplots(figsize=(6, 3))
    n, bins, patches = ax.hist(
        Z, bins=256, ec='white', fc='none', histtype='step', density=True)

    ax.set_title(f'{min} : {max}', fontsize=12)

    #txt = ax.text(5, 30, f'{min_thres} : {max_thres}', fontsize=12)
    axvline1 = ax.axvline(min, color='white',
                          linestyle='--', lw=1, label="min")
    axvline2 = ax.axvline(max, color='white',
                          linestyle='--', lw=1, label="max")

    # Define aparência do histograma, fundo preto e informações brancas
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

    # Posição da janela com o histograma
    def move_figure(f, x, y):
        backend = matplotlib.get_backend()
        if backend == 'TkAgg':
            f.canvas.manager.window.wm_geometry("+%d+%d" % (x, y))
        elif backend == 'WXAgg':
            f.canvas.manager.window.SetPosition((x, y))
        else:
            f.canvas.manager.window.move(x, y)

    move_figure(fig, 700, 375)

    fig.canvas.draw_idle()

    # Encerra o programa ao fechar a janela do histograma
    def on_close(event):
        sys.exit()

    fig.canvas.mpl_connect('close_event', on_close)

    fig.canvas.mpl_connect('button_press_event', on_click)

    plt.show()
