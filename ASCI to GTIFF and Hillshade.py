#This Script reads ASCII files, set Projection and conv. to GTIFF and adds Hillshades
#Just for Fun and might be usefull

#Imports

import numpy as np
import math
import matplotlib.pyplot as plt
from osgeo import osr, gdal

#Drvers and Proj
drv = gdal.GetDriverByName('GTiff')
srs = osr.SpatialReference()
srs.ImportFromEPSG(21781)

#Functions

#Convert Asci to GTIFF inkl. Proj.
def convertASCIItoGTIFF (intifgrit):
    ingrit = gdal.Open(intifgrit)
    outras = drv.CreateCopy(intifgrit.replace('.asc','.tif'), ingrit)
    outras.SetProjection(srs.ExportToWkt())
    del ingrit
    del outras

#Add Hillshade,Slope, etc to DEM's comes out Byt, possible to convert to Float32
def DEMprocess (intifras, outfile, mode):
    inras=gdal.Open(intifras)
    processing=gdal.DEMProcessing(outfile, inras,mode)
    return processing
    del inras


#SetWorkingdirectory

wd= "C:/Users/jonas/desktop"

convertASCIItoGTIFF(wd+'/dhm_1.asc')
DEMprocess(wd+'/dhm_1.tif',wd+'/'+'HS_dhm_1.tif','Hillshade')


