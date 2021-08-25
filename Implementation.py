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
import pandas as pd

#Functions

#Read Raster as Array
def getRasterBand (ds, band=1, access=0):
    band=ds.GetRasterBand(1).ReadAsArray()
    return band

#Substract of the two arrays and copy to new file
def createRasterFromCopy(dst,ds,data,driverFmt='GTiff'):
    driver=gdal.GetDriverByName(driverFmt)
    outds=driver.CreateCopy(dst,ds,strict=0)
    outds.GetRasterBand(1).WriteArray(data)
    ds=None
    outds=None

#Workspace

ws = input('create a workspace folder and enter path of your workspace(ws):')

#Drivers and Proj(EPSG 21781 for LV03)
drv = gdal.GetDriverByName('GTiff')
srs = osr.SpatialReference()
srs.ImportFromEPSG(21781)

#Enter the Filname of the merged swissALTI3D file
FileName=input('Filename of the merged SwissALTI3D data in ws (e.g. glacier_tsanfleuron.tif):')


glacier = input('name of glacier(same writen as in Glacier Outline Shape File(Check Attribute Table in GIS)!!!):')
#Open dhm25
dhm25=gdal.Open(ws+'/dhm25_grid_raster.tif')

#Open and Edit ALTI3D(Resample and Clip)
print('edit and open swissALTI3D')
alti3d = gdal.Open(ws + f'/{FileName}')
transform = dhm25.GetGeoTransform()
ba_edit_alti3d =gdal.Warp(ws +f'/ba_edit_{FileName}', alti3d, xRes=transform[1], yRes=transform[1], resampleAlg="bilinear", cutlineDSName=ws + "/ba_outline/outline_98_2.shp", cutlineWhere=f"name='{glacier}'", cropToCutline=True, dstNodata=np.nan)
ba_edit_alti3d =gdal.Open(ws + f'/ba_edit_{FileName}')

#Edit DEM25(Reproject and Clip)
print('edit dhm25')
ba_edit_dhm25 = gdal.Warp(ws+'/'+'ba_edit_dhm25.tif', dhm25, dstSRS='EPSG:2056',cutlineDSName=ws+"/ba_outline/outline_98_2.shp", cutlineWhere=f"name='{glacier}'", cropToCutline=True, dstNodata=np.nan )
ba_edit_dhm25 = gdal.Open(ws+'/'+'ba_edit_dhm25.tif')

NewFile = ws+'/'+f'ba_substract_{FileName}'

#Calculate Diffrence and write to a new Tiff


Old=getRasterBand(ba_edit_dhm25)
New=getRasterBand(ba_edit_alti3d)
Diff=Old-New

createRasterFromCopy(NewFile, ba_edit_alti3d, Diff)

ba_substract=gdal.Open(ws+'/'+f'ba_substract_{FileName}')


#Read as Array
ba_substractArray = ba_substract.GetRasterBand(1).ReadAsArray()
ba_alti3DArray = ba_edit_alti3d.ReadAsArray()

#Masking the two dhm's

ba_masked_substract= np.ma.masked_invalid(ba_substractArray)
ba_masked_alti3D= np.ma.masked_invalid(ba_alti3DArray)

#Merge the two Masks
ba_multimask = np.ma.mask_or(np.ma.getmask(ba_masked_substract), np.ma.getmask(ba_masked_alti3D))

ba_substract_Final_Mask=np.ma.array(ba_substractArray, mask=ba_multimask, fill_value=np.nan ).compressed()
ba_alti3D_Final_Mask=np.ma.array(ba_alti3DArray, mask=ba_multimask,fill_value=np.nan).compressed()

#Make Dataframe dh/DHM
ba_df =  pd.DataFrame(np.column_stack([ba_substract_Final_Mask, ba_alti3D_Final_Mask]), columns=['dh','DHM'])
ba_df_sort = ba_df.sort_values('dh')

#Avarage elevation Change between 1998 and 2016
dh_mean =ba_df_sort['dh'].mean()

#dv = dh x A98

#Glacier Area 1998
A98 =(ba_df['dh'].count()) * 625

#dv in m^3

dv = -dh_mean * A98


#Constant according to Densitiy of Vol. Change (fdv) = 0.85

fdv= 0.85

# A = Average Area between 1998 and 2016 ((A98 + A16)/2))

#A 16 from SGI

A16 = 2442977

A= (A98 + A16)/2

#dt = time between dhm25 and alti3D

dt= 18

#BA = (dv * fdv) / (A * dt) in m w.a yr^-1

BA = (dv * fdv) / (A * dt)