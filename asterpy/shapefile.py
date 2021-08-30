from re import A
import numpy as np
from osgeo import gdal, ogr, osr
from shapely.geometry.polygon import Polygon
import subprocess
import os
import cv2 as cv2
import os.path
import shapely
import asterpy as ap

shapely.speedups.disable()

def make_polygon(file, path):
    print(f"Criando shapefile da imagem {file}")

    shape_dir = path + '08_Shapes\\'
    index_dir = path + '02_Indices\\'
    phyll_dir = '01_Phyll\\'

    if not os.path.isfile(index_dir + phyll_dir + file + '_Phyll.tif'):
        ap.layer_stack(file, path)
        ap.index_calc(file, path)

    # Se o arquivo do shapefile existir a função retorna
    if os.path.isfile(shape_dir + file + '.shp'):
        return 1
    
    print(f"Criando shapefile da cena {file}")

    # Pega imagem a partir do índice
    img_dir = index_dir + phyll_dir + file + '_Phyll.tif'

    def convert_to_32723(x, y):
        InSR = osr.SpatialReference()
        InSR.ImportFromEPSG(32724)
        OutSR = osr.SpatialReference()
        OutSR.ImportFromEPSG(32723)

        Point = ogr.Geometry(ogr.wkbPoint)
        Point.AddPoint(x,y) # Passa coordenadas para converter
        Point.AssignSpatialReference(InSR)    # Informa o sistema de coordenada de entrada
        Point.TransformTo(OutSR)              # Informa o sistema de coordenada de saída
        return Point.GetX(), Point.GetY()

    def pixel2coord(x, y, arg):
        if arg == 1:
            xoff, a, b, yoff, d, e = ds.GetGeoTransform()   
            xp = a * x + b * y + xoff
            yp = d * x + e * y + yoff
            return(convert_to_32723(xp, yp))
        else:
            xoff, a, b, yoff, d, e = ds.GetGeoTransform()   
            xp = a * x + b * y + xoff
            yp = d * x + e * y + yoff
            return(xp, yp)

    # Abre imagem raster
    ds = gdal.Open(img_dir)

    # Le array da imagem
    Z = ds.ReadAsArray()

    Z = np.ma.masked_invalid(Z)

    min_thres = (Z[np.where(Z != 0)]).min()
    out_img = 'white_image.tif'

    # Converte imagem para preto e branco
    subprocess.call(['gdal_translate.exe', '-quiet','-ot', 'Byte', '-scale', '0', str(min_thres), img_dir, out_img])

    # Le imagem em escala de cinza
    img = cv2.imread(out_img, 0)

    # Enconta o contorno da imagem
    contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contour = contours[0]
    perimeter = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.05 * perimeter, True)

    proj = osr.SpatialReference(wkt=ds.GetProjection())

    if proj.GetAttrValue('AUTHORITY',1) == '32724':
        need_conversion = 1
    else:
        if proj.GetAttrValue('AUTHORITY',1) != '32723':
            print("ERRO - EPSG NÂO CONFIGURADO")
            os.sys.exit()
        else:
            need_conversion = 0

    # Converte as coordenadas dos pixels da imagem para coordenadas geográficas 
    ext = (pixel2coord(approx[0][0][0], approx[0][0][1], need_conversion), pixel2coord(approx[1][0][0], approx[1][0][1], need_conversion),
    pixel2coord(approx[2][0][0], approx[2][0][1], need_conversion), pixel2coord(approx[3][0][0], approx[3][0][1], need_conversion))

    x = [ext[3][0], ext[2][0], ext[1][0], ext[0][0]]
    y = [ext[3][1], ext[2][1], ext[1][1], ext[0][1]]

    # Create a polygon shapefile
    #Shapely geometry
    poly = Polygon([(x[0], y[0]), (x[1], y[1]), (x[2], y[2]), (x[3], y[3])])

    f = open(shape_dir + file + "_coords.txt", "w")
    f.write(str(ext))
    f.close()

    # Converte para shapefile com o OGR
    driver = ogr.GetDriverByName("Esri Shapefile")

    ds = driver.CreateDataSource(shape_dir + file + ".shp")
    layer = ds.CreateLayer('', None, ogr.wkbPolygon)
    
    # Adiciona atributos
    field_serial = ogr.FieldDefn('serial', ogr.OFTString)
    field_serial.SetWidth(7)
    layer.CreateField(field_serial)

    field_name = ogr.FieldDefn('name', ogr.OFTString)
    field_name.SetWidth(len(file))
    layer.CreateField(field_name)

    field_date = ogr.FieldDefn('date', ogr.OFTString)
    field_date.SetWidth(10)
    layer.CreateField(field_date)

    field_time = ogr.FieldDefn('time', ogr.OFTString)
    field_time.SetWidth(9)
    layer.CreateField(field_time)

    field_period = ogr.FieldDefn('period', ogr.OFTString)
    field_period.SetWidth(7)
    layer.CreateField(field_period)

    infos = file.split('_')[2]
    date = f"{infos[5:7]}/{infos[3:5]}/{infos[7:11]}"
    time = f"{infos[11:13]}:{infos[13:15]}:{infos[15:17]}"

    hour = infos[11:13]
    if int(hour) >= 6 and int(hour) < 18:
        period = 'dia'
    else:
        period = 'noite'

    feature = ogr.Feature(layer.GetLayerDefn())
    feature.SetField('serial', file.split('_')[4])
    feature.SetField('name', file)
    feature.SetField('date', date)
    feature.SetField('time', time)
    feature.SetField('period', period)

    # Criar geometria a partir do objeto Shape
    geom = ogr.CreateGeometryFromWkb(poly.wkb)
    feature.SetGeometry(geom)

    layer.CreateFeature(feature)

    layer = feature = geom = None  # limpa variáveis

    # apaga o arquivo da imagem 
    os.remove(out_img)

    print(f"Shapefile de {file} criado!")
    return 0 