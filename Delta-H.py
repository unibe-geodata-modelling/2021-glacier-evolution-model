from osgeo import osr, gdal, ogr
import numpy as np
import math
import matplotlib.pyplot as plt
import fiona
import pyproj
import rtree
import shapely
import geopandas as gpd

#Workspace
ws = 'C:/Users/jonas/Desktop/workspace/'

#Drvers and Proj(EPSG 21781 for LV03)
drv = gdal.GetDriverByName('GTiff')
srs = osr.SpatialReference()
srs.ImportFromEPSG(21781)


#Convert DEM25 .Asc to GTIFF inkl. Proj.
def convertASCIItoGTIFF (intifgrit):
    ingrit = gdal.Open(intifgrit)
    outras = drv.CreateCopy(intifgrit.replace('.asc','.tif'), ingrit)
    outras.SetProjection(srs.ExportToWkt())
    del ingrit
    del outras

convertASCIItoGTIFF(ws+'/dhm25_grid_raster.asc')
DEM25=gdal.Open(ws+'/dhm25_grid_raster.tif')

#Open and Edit ALTI3D(Resample and Clip)

Alti3D = gdal.Open(ws+'/glacier_tsanfleuron.tif')
Alti3D_Edit=gdal.Warp(ws+'/glacier_tsanfleuron_Edit.tif',Alti3D, xRes=25, yRes=25, resampleAlg="bilinear", cutlineDSName=ws+"/Glacier_Outlines/SGI_2016_glaciers.shp", cutlineWhere="name='Glacier de Tsanfleuron'", cropToCutline=True, dstNodata=np.nan )
#Alti3D_Edit=gdal.Open(ws+'/glacier_tsanfleuron_Edit.tif')

#Edit DEM25(Reproject and Clip)

DEM25_Edit = gdal.Warp(ws+'/'+'DEM25_Edit.tif', DEM25, dstSRS='EPSG:2056',cutlineDSName=ws+"/Glacier_Outlines/SGI_2016_glaciers.shp", cutlineWhere="name='Glacier de Tsanfleuron'", cropToCutline=True, dstNodata=np.nan )
#DEM25_Edit=gdal.Open(ws+'/'+'DEM25_Edit.tif')

#Substract DEM25 - ALTI3D

NewFile = ws+'/'+'Substract.tif'

#Read DEM25 and ALTI3D as Array
def getRasterBand (ds, band=1, access=0):
    band=ds.GetRasterBand(1).ReadAsArray()
    return band

#WriteDiffrence to a new Tiff
def createRasterFromCopy(dst,ds,data,driverFmt='GTiff'):
    driver=gdal.GetDriverByName(driverFmt)
    outds=driver.CreateCopy(dst,ds,strict=0)
    outds.GetRasterBand(1).WriteArray(data)
    ds=None
    outds=None

Old=getRasterBand(DEM25_Edit)
New=getRasterBand(Alti3D_Edit)
Diff=Old-New

createRasterFromCopy(NewFile,Alti3D_Edit,Diff)

Subtract=gdal.Open(NewFile)








