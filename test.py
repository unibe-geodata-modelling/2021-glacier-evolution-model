#test repository

##hallo welt

#second check
# read ascii file
from osgeo import osr, gdal
import numpy as np
import math
import matplotlib.pyplot as plt

drv = gdal.GetDriverByName('GTiff')
srs = osr.SpatialReference()
srs.ImportFromEPSG(21781) #for LV03 coordinate system and EPSG:2056 for LV95 Swiss cordinate system
gtiff_driver=gdal.GetDriverByName("GTiff")



#Tiff to Array (Add file path)
ds = gdal.Open('C:/Users/jonas/desktop/glacier_tsanfleuron.tif')
inband = ds.GetRasterBand(1)
outarr = inband.ReadAsArray()
ds.GetProjectionRef()
plt.imshow(outarr)

#could make hillshade but cant run it in QGIS
hillshade = gdal.DEMProcessing('C:/Users/jonas/desktop/HSTEST.tif',ds,'Hillshade',format='GTiff')
hillshadeAR = hillshade.GetRasterBand(1).ReadAsArray()
plt.imshow(hillshadeAR)

hillshade.GetProjectionRef()

#with running in this function i could make it run in QGIS
def convertarrtotif(arr, outfile, tifdatatype, referenceraster, nodatavalue):
    ds_in=gdal.Open(referenceraster)
    inband=ds_in.GetRasterBand(1)
    gtiff_driver=gdal.GetDriverByName("GTiff")
    ds_out = gtiff_driver.Create(outfile, inband.XSize, inband.YSize, 1, tifdatatype)
    ds_out.SetProjection(ds_in.GetProjection())
    ds_out.SetGeoTransform(ds_in.GetGeoTransform())
    outband=ds_out.GetRasterBand(1)
    outband.WriteArray(arr)
    outband.SetNoDataValue(nodatavalue)
    ds_out.FlushCache()
    del ds_in
    del ds_out
    del inband
    del outband

workingdiretory= "C:/Users/jonas/desktop"
# create a reference raster to set extent cellsizes and georeferencing
referenceraster='C:/Users/jonas/desktop/glacier_tsanfleuron.tif'
referencetifraster=gdal.Open(referenceraster)
referencetifrasterband=referencetifraster.GetRasterBand(1)
referencerasterProjection=referencetifraster.GetProjection()
ncols=referencetifrasterband.XSize
nrows=referencetifrasterband.YSize
indatatype=referencetifrasterband.DataType
NODATA_value=-9999

convertarrtotif(hillshadeAR, workingdiretory+"/"+"HS_Tsanfleuron.tif", 5, referenceraster, NODATA_value)
