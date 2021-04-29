from osgeo import osr, gdal
drv = gdal.GetDriverByName('GTiff')
srs = osr.SpatialReference()
srs.ImportFromEPSG(21781) #for LV03 coordinate system and EPSG:2056 for LV95 Swiss cordinate system
gtiff_driver=gdal.GetDriverByName("GTiff")

#*************************************************************
#functions
#*************************************************************
def convert_tif_to_array(intifraster):
    inras = gdal.Open(intifraster)
    inband = inras.GetRasterBand(1)
    outarr = inband.ReadAsArray()
    return outarr
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
# *************************************************************
#end functions
# *************************************************************
workingdiretory="C:/temp"
create a reference raster to set extent cellsizes and georeferencing
referenceraster="C:/temp/dhm25.tif"
referencetifraster=gdal.Open(referenceraster)
referencetifrasterband=referencetifraster.GetRasterBand(1)
referencerasterProjection=referencetifraster.GetProjection()
ncols=referencetifrasterband.XSize
nrows=referencetifrasterband.YSize
indatatype=referencetifrasterband.DataType
NODATA_value=-9999

#read a raster dataset
print("read the raster...")
rasterarray=convert_tif_to_array(workingdiretory+"/myrasterfile.tif")

#do something with the array
rasterarray2=rasterarray*2.0 #be aware what happens with the nodata values, check if nodata values are also converted or if they must be excluded from processsing. 

#write the output
print("write the output....")
convertarrtotif(rasterarray2, workingdiretory+"/"+"outputrasterfile.tif", 5, referenceraster, NODATA_value)

