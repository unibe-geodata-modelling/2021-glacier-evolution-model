#Delta-H Final Script



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

#ASCII TO GTIFF
def convertASCIItoGTIFF (intifgrit):
    ingrit = gdal.Open(intifgrit)
    outras = drv.CreateCopy(intifgrit.replace('.asc','.tif'), ingrit)
    outras.SetProjection(srs.ExportToWkt())
    del ingrit
    del outras

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

#Normalize dhm and dh
def normalize_DHM(dhm):
    dhm_n = dhm.copy()
    dhm_n = (dhm.max() - dhm)/(dhm.max() - dhm.min())
    return dhm_n
def normalize_dh (dh):
    dh_n = dh.copy()
    dh_n = dh/dh.max()
    return dh_n


#Workspace: Define a Workspace for the following steps.
ws = input('create a workspace folder and enter path of your workspace(ws):')


################################################PREPROCESSING###########################################################

#Download glacier outlines
print('download the glacier_outlines folder from Drive and safe it to ws')

#Download dhm25 and Safe to ws
print("download the dhm25_grid_raster from Drive and Save it to ws")


#Select the Glacier
glacier = input('name of glacier(same writen as in Glacier Outline Shape File(Check Attribute Table in GIS)!!!):')



#Drivers and Proj(EPSG 21781 for LV03)
drv = gdal.GetDriverByName('GTiff')
srs = osr.SpatialReference()
srs.ImportFromEPSG(21781)




#Convert DHM25 .Asc to GTIFF inkl. Proj.
print('processing projection and format of dhm25 of Switzerland ...have some patience please')
convertASCIItoGTIFF(ws+'/dhm25_grid_raster.asc')
dhm25=gdal.Open(ws+'/dhm25_grid_raster.tif')

#Download swissALTI3D and merge in QGIS

print('download swissALTI3D of the selected Glacier as GTIFF from: https://www.swisstopo.admin.ch/de/geodata/height/alti3d.html')
print('merge the files in QGIS and safe it to ws')

#Enter the Filname of the merged swissALTI3D file
FileName=input('Filename of the merged SwissALTI3D data in ws (e.g. glacier_tsanfleuron.tif):')

#Open and Edit ALTI3D(Resample and Clip)
print('edit and open swissALTI3D')
alti3d = gdal.Open(ws + f'/{FileName}')
transform = dhm25.GetGeoTransform()
edit_alti3d =gdal.Warp(ws +f'/edit_{FileName}', alti3d, xRes=transform[1], yRes=transform[1], resampleAlg="bilinear", cutlineDSName=ws + "/glacier_outlines/SGI_2016_glaciers.shp", cutlineWhere=f"name='{glacier}'", cropToCutline=True, dstNodata=np.nan)
edit_alti3d =gdal.Open(ws + f'/edit_{FileName}')


#Edit DEM25(Reproject and Clip)
print('edit dhm25')
edit_dhm25 = gdal.Warp(ws+'/'+'edit_dhm25.tif', dhm25, dstSRS='EPSG:2056',cutlineDSName=ws+"/glacier_outlines/SGI_2016_glaciers.shp", cutlineWhere=f"name='{glacier}'", cropToCutline=True, dstNodata=np.nan )
edit_dhm25 = gdal.Open(ws+'/'+'edit_dhm25.tif')


#Substract DEM25(Old) - ALTI3D(Modern)

NewFile = ws+'/'+f'substract_{FileName}'

#Calculate Diffrence and write to a new Tiff


Old=getRasterBand(edit_dhm25)
New=getRasterBand(edit_alti3d)
Diff=Old-New

createRasterFromCopy(NewFile, edit_alti3d, Diff)

substract=gdal.Open(ws+'/'+f'substract_{FileName}')





print('Now you have a file called Substract_(your file name) in the ws folder. There you see the alteration of glacier thikness '
      'between the older dhm25 and the modern swissAlti3D,it s 18 years.')

############################################################DELTA-H PARAMETRIZATION#####################################

print('Processing of Delta-H Parametrization')
#Read as Array
substractArray = substract.GetRasterBand(1).ReadAsArray()
alti3DArray = edit_alti3d.ReadAsArray()

#Mask the arrays

masked_substract= np.ma.masked_invalid(substractArray)
masked_alti3D= np.ma.masked_invalid(alti3DArray)


hypsometry, bins = np.histogram(masked_alti3D.compressed(), bins=int ((masked_alti3D.max()-masked_alti3D.min())/10))
up_lim= bins[1:]
low_lim=bins[0:-1]
up_lim
low_lim

#Merge the two Masks
multimask = np.ma.mask_or(np.ma.getmask(masked_substract), np.ma.getmask(masked_alti3D))

substract_Final_Mask=np.ma.array(substractArray, mask=multimask, fill_value=np.nan ).compressed()
alti3D_Final_Mask=np.ma.array(alti3DArray, mask=multimask,fill_value=np.nan).compressed()

#Make Dataframe dh/DHM
df =  pd.DataFrame(np.column_stack([substract_Final_Mask, alti3D_Final_Mask]), columns=['dh','DHM'])

#Make Elevation Bands
df_sort = df.sort_values('DHM')
ind = np.digitize(df_sort['DHM'], bins)

df_band=df_sort.groupby(ind).mean()

#Calculate the Area of each Band
band_area = []
for i in hypsometry:
    band_area.append(i * 625)

#Separating dh and DHM
dhm_df = df_band['DHM']
dh_df = df_band['dh']

#plt.plot(dhm_df,dh_df)

#smoth
#dhm_smoth_df = dhm_df.rolling(window=3, min_periods=1).mean()
dh_smoth_df = dh_df.rolling(window=3, min_periods=1).mean()

#plt.plot(dhm_smoth_df, dh_smoth_df)



#Normalize dhm and dh
#dhm_smoth_df_n = normalize_DHM(dhm_smoth_df)
dhm_df_n = normalize_DHM(dhm_df)
dh_smoth_df_n = normalize_dh(dh_smoth_df)



#plot deltaH and elevation Range

plt.plot(dhm_df_n, dh_smoth_df_n)
plt.gca().invert_yaxis()
plt.title(f'delta-H {glacier}')
plt.xlabel('Normalized elevation range')
plt.ylabel('Normalized ice thickness change')

#Save Plot
plt.savefig(ws+f'/delta_H_{glacier}.png')
print('A graph of the parametrization of your selected glacier is saved in your ws ')

#Save Files as txt

## normalized elevation range, normalized ice tickness change, band_area

parametrization = pd.DataFrame( np.column_stack([dhm_df_n , dhm_df, dh_smoth_df_n, dh_smoth_df, low_lim, up_lim, band_area]), columns=['normalized_elevation_range', 'band_elevation', 'normalized_ice_thickness_change', 'ice_thickness_change', 'low_lim', 'up_lim', 'band-area'])

np.savetxt(ws+f'/deltaH_{glacier}.txt', parametrization, delimiter = ';', fmt= '%.5f', header='normalized_elevation_range ; band_elevation ; normalized_ice_thickness_change  ; ice_thickness_change; low_lim; up_lim;  band_area')

print('Txt file of the parametrization is saved in your ws')


#####################################################################IMPLEMENTATION##################################################################################################

################################################################Calculate Ba(Massbalance)###########################################################################################

