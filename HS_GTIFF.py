
from osgeo import osr, gdal
import numpy as np
import math
import matplotlib.pyplot as plt

drv = gdal.GetDriverByName('GTiff')
srs = osr.SpatialReference()
srs.ImportFromEPSG(21781) #for LV03 coordinate system and EPSG:2056 for LV95 Swiss cordinate system
gtiff_driver=gdal.GetDriverByName("GTiff")

workingdirectory= "C:/Users/jonas/desktop/glacier_model_inputdata"


#Tiff to Array (Add file path)
ds = gdal.Open(workingdirectory+'/'+'glacier_tsanfleuron.tif')
inband = ds.GetRasterBand(1)
outarr = inband.ReadAsArray()

#View DEM
plt.imshow(outarr)


#Make Hillshade

hillshade = gdal.DEMProcessing(workingdirectory+'/'+'HS_glacier_tsanfleuron.tif',ds,'Hillshade')

#Change Type to Float(Would be Nice to bring it in the upper Function????

hillshade_float = gdal.Translate(workingdirectory+'/'+'HS_glacier_tsanfleuron_float.tif', hillshade, outputType = 6)

#Make array and Plot

hillshadeAR = hillshade_float.GetRasterBand(1).ReadAsArray()
plt.imshow(hillshadeAR)


#Close Datasets

drv=srs=workingdirectory=ds=inband=outarr=hillshade=hillshade2=hillshadeAR=hillshade_float= None