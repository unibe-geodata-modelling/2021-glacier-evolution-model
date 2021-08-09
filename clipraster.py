#Imports

from osgeo import osr, gdal, ogr
import numpy as np
import math
import matplotlib.pyplot as plt
import fiona
import pyproj
import rtree
import shapely
import geopandas as gpd

#Set WS

ws = 'C:/Users/jonas/Desktop/glacier_model_inputdata/Glacier_Outlines'

#Read Shapefile(All Data have to be in the same folder) if not -> Error

ch_glaciers=gpd.read_file(ws+"/"+"SGI_2016_glaciers.shp")

ch_glaciers.head()
ch_glaciers.columns
#Read DEM
DEM = gdal.Open('C:/Users/jonas/Desktop/glacier_model_inputdata/glacier_tsanfleuron.tif')

#Check Projections (EPSG 2056 for ALTI3D)
ch_glaciers.crs

#Clip(warp(destination,DEM to clip, cutlineDSName= shapefile, cutlineWhere=(select in attributtable))

dsClip=gdal.Warp('C:/Users/jonas/Desktop/glacier_model_inputdata/clip_glacier.tif', DEM, cutlineDSName=ws+"/"+"SGI_2016_glaciers.shp", cutlineWhere="name='Glacier de Tsanfleuron'", cropToCutline=True, dstNodata=np.nan )

dsClip=None



