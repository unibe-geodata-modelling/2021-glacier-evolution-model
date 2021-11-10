#Script for Implementation.





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

#Normalize dhm and dh
def normalize_DHM(dhm):
    dhm_n = dhm.copy()
    dhm_n = (dhm.max() - dhm)/(dhm.max() - dhm.min())
    return dhm_n
def normalize_dh (dh):
    dh_n = dh.copy()
    dh_n = dh/dh.max()
    return dh_n


#Workspace: Enter the path of a separate workspace for the implementation

ws = 'C:/Users/jonas/Desktop//workspace_implementation'

#Drivers and Proj(EPSG 21781 for LV03)
drv = gdal.GetDriverByName('GTiff')
srs = osr.SpatialReference()
srs.ImportFromEPSG(21781)


#########################################################Calculating Geodetic Mass Balance Change (Ba) according to Fischer M. et al. 2015##############################################

#Glacier to model.
glacier = 'Glacier de Tsanfleuron'

#Open and edit files

#Open dhm25
#dhm25=gdal.Open(ws+'/dhm25_grid_raster.tif')

#Edit DEM25(Reproject and Clip) with the 1998 glacier extend
#print('edit dhm25')
#ba_edit_dhm25 = gdal.Warp(ws+'/'+'ba_edit_dhm25.tif', dhm25, dstSRS='EPSG:2056',cutlineDSName=ws+"/98_outline/outline_98_2.shp", cutlineWhere=f"name='{glacier}'", cropToCutline=True, dstNodata=np.nan )
ba_edit_dhm25 = gdal.Open(ws+'/'+'ba_edit_dhm25.tif')


#Open and Edit ALTI3D(Resample and Clip) with the 1998 glacier extend
#print('edit and open swissALTI3D')
#alti3d = gdal.Open(ws+'/glacier_tsanfleuron.tif')
#transform = dhm25.GetGeoTransform()
#ba_edit_alti3d =gdal.Warp(ws +'/ba_edit_glacier_tsanfleuron.tif', alti3d, xRes=transform[1], yRes=transform[1], resampleAlg="bilinear", cutlineDSName=ws + "/98_outline/outline_98_2.shp", cutlineWhere=f"name='{glacier}'", cropToCutline=True, dstNodata=np.nan)
ba_edit_alti3d =gdal.Open(ws + '/ba_edit_glacier_tsanfleuron.tif')

#Open the parametrication .txt file
parametrication = pd.read_csv(ws+'/deltaH_Glacier de Tsanfleuron.txt', sep=';')


#Open the Edit Alti3D file with the 2016 glacier extend
edit_alti3d = gdal.Open(ws + f'/edit_{FileName}')


#Open and edit the glacier bed file
glacier_bed = gdal.Open(ws + '\GlacierBed.tif')
edit_glacier_bed =gdal.Warp(ws +f'/glacier_bed_{FileName}', glacier_bed, xRes=25, yRes=25, resampleAlg="bilinear", cutlineDSName=ws + "/glacier_outlines/SGI_2016_glaciers.shp", cutlineWhere=f"name='{glacier}'", cropToCutline=True, dstNodata=np.nan)
edit_glacier_bed =gdal.Open(ws + f'/glacier_bed_{FileName}')



#Calculate volume change from 1998 to 2016

#NewFile = ws+'/'+f'ba_substract_{FileName}'

#Calculate Diffrence and write to a new Tiff


#Old=getRasterBand(ba_edit_dhm25)
#New=getRasterBand(ba_edit_alti3d)
#Diff=Old-New

#createRasterFromCopy(NewFile, ba_edit_alti3d, Diff)

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

######################################################Equation (1) in Fischer et al. 2015######################################################

#Avarage elevation Change between 1998 and 2016.
dh_mean =ba_df_sort['dh'].mean()

#dv = dh_mean x A98

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


############################################Calculate fs according to Huss et al. 2010 Eq. 2########################################################################################

#Ba = fs * pice * Sum (Ai * dhi)

#fs= Ba/fs*pic*Sum (Ai* dhi)


#Band Area * normalized elevation range

((parametrication.iloc[:,2] * parametrication.iloc[:,6]).sum())* 920

fs= (BA* 997 * 2442977) / (((parametrication.iloc[:,2] * parametrication.iloc[:,6]).sum())* 920)


##############################################################Calculate h1################################################################################################


#Read the alti3d file with 2016 glacier extend and the glacier bed file as an array

alti3DArray = edit_alti3d.ReadAsArray()
edit_glacier_bed_array = edit_glacier_bed.ReadAsArray()




#####Update alti 3d array band by band with dh# and compare with glacier bed!!!!!

'''''Band1 = np.where((bins[0] <= alti3DArray) & (alti3DArray >= bins[1]),alti3DArray, alti3DArray+fs*parametrication.iloc[0,1])
Band2 = np.where(alti3DArray >= bins[2],Band1, alti3DArray+fs*parametrication.iloc[1,1])
Band3 = np.where(alti3DArray >= bins[3],Band2, alti3DArray+fs*parametrication.iloc[2,1])
Band4 = np.where(alti3DArray >= bins[4],Band3, alti3DArray+fs*parametrication.iloc[3,1])
Band5 = np.where(alti3DArray >= bins[5],Band4, alti3DArray+fs*parametrication.iloc[4,1])
Band6 = np.where(alti3DArray >= bins[6],Band5, alti3DArray+fs*parametrication.iloc[5,1])
Band7 = np.where(alti3DArray >= bins[7],Band6, alti3DArray+fs*parametrication.iloc[6,1])
Band8 = np.where(alti3DArray >= bins[8],Band7, alti3DArray+fs*parametrication.iloc[7,1])
Band9 = np.where(alti3DArray >= bins[9],Band8, alti3DArray+fs*parametrication.iloc[8,1])
Band10 = np.where(alti3DArray >=bins[10],Band9, alti3DArray+fs*parametrication.iloc[9,1])
Band11= np.where(alti3DArray >= bins[11],Band10, alti3DArray+fs*parametrication.iloc[10,1])
Band12= np.where(alti3DArray >= bins[12],Band11, alti3DArray+fs*parametrication.iloc[11,1])
Band13= np.where(alti3DArray >= bins[13],Band12, alti3DArray+fs*parametrication.iloc[12,1])
Band14= np.where(alti3DArray >= bins[14],Band13, alti3DArray+fs*parametrication.iloc[13,1])
Band15 = np.where(alti3DArray >=bins[15],Band14, alti3DArray+fs*parametrication.iloc[14,1])
Band16 = np.where(alti3DArray >=bins[16],Band15, alti3DArray+fs*parametrication.iloc[15,1])
Band17 = np.where(alti3DArray >=bins[17],Band16, alti3DArray+fs*parametrication.iloc[16,1])
Band18 = np.where(alti3DArray >=bins[18],Band17, alti3DArray+fs*parametrication.iloc[17,1])
Band19 = np.where(alti3DArray >=bins[19],Band18, alti3DArray+fs*parametrication.iloc[18,1])
Band20 = np.where(alti3DArray >= bins[20],Band19, alti3DArray+fs*parametrication.iloc[19,1])
Band21= np.where(alti3DArray >= bins[21],Band20, alti3DArray+fs*parametrication.iloc[20,1])
Band22= np.where(alti3DArray >= bins[22],Band21, alti3DArray+fs*parametrication.iloc[21,1])
Band23= np.where(alti3DArray >= bins[23],Band22, alti3DArray+fs*parametrication.iloc[22,1])
Band24= np.where(alti3DArray >= bins[24],Band23, alti3DArray+fs*parametrication.iloc[23,1])
Band25= np.where(alti3DArray >= bins[25],Band24, alti3DArray+fs*parametrication.iloc[24,1])
Band26= np.where(alti3DArray >= bins[26],Band25, alti3DArray+fs*parametrication.iloc[25,1])
Band27= np.where(alti3DArray >= bins[27],Band26, alti3DArray+fs*parametrication.iloc[26,1])
Band28= np.where(alti3DArray >= bins[28],Band27, alti3DArray+fs*parametrication.iloc[27,1])
Band29= np.where(alti3DArray >= bins[29],Band28, alti3DArray+fs*parametrication.iloc[28,1])
Band30= np.where(alti3DArray >= bins[30],Band29, alti3DArray+fs*parametrication.iloc[29,1])
Band31= np.where(alti3DArray >= bins[31],Band30, alti3DArray+fs*parametrication.iloc[30,1])
Band32= np.where(alti3DArray >= bins[32],Band31, alti3DArray+fs*parametrication.iloc[31,1])
Band33= np.where(alti3DArray >= bins[33],Band32, alti3DArray+fs*parametrication.iloc[32,1])
Alti_H1 = np.where(alti3DArray <= bins[34],Band33, alti3DArray+fs*parametrication.iloc[33,1])'''''


Alti_H1 = None
for index in range(len(parametrication)):
    if index == 0:
        Alti_H1 = np.where(((alti3DArray >= (parametrication.iloc[index, 4])) & (alti3DArray <= (parametrication.iloc[index, 5]))), alti3DArray + fs * parametrication.iloc[index, 2], alti3DArray)

    else:
        Alti_H1 = np.where(((alti3DArray >= (parametrication.iloc[index, 4])) & (alti3DArray <= (parametrication.iloc[index, 5]))), alti3DArray + fs * parametrication.iloc[index, 2], Alti_H1)

Alti_H1_Final = np.where(Alti_H1 >= edit_glacier_bed_array, Alti_H1, np.nan)
print(Alti_H1_Final)


#Difference

substract_1 = alti3DArray-Alti_H1_Final



########################################################Calculae new fs according to alti_H1_final#########################################################################

#Mask alti_H1_Final

masked_alti_H1= np.ma.masked_invalid(Alti_H1_Final)



#Elevation Bands
bins = list (parametrication.iloc[:,4])

bins.append(parametrication.iloc[-1,5])




#Hypsometrie

hypsometry, bins = np.histogram(masked_alti_H1.compressed(), bins=bins)

#Area
band_area_h1 = []
for i in hypsometry:
    band_area_h1.append(i * 625)

#Fs_H1

fs_H1 = (BA* 997 * 2442977) / (((parametrication.iloc[:,2] * band_area_h1).sum())* 920)


#Alti_H2
Alti_H2 = None
for index in range(len(parametrication)):

    Alti_H2 = np.where(((Alti_H1_Final >= (parametrication.iloc[index, 4])) & (Alti_H1_Final <= (parametrication.iloc[index, 5]))), Alti_H1_Final + fs_H1 * parametrication.iloc[index, 2], Alti_H2)

Alti_H2_float = np.array(Alti_H2, dtype= float)
Alti_H2_Final = np.where(Alti_H2_float >= edit_glacier_bed_array, Alti_H2_float, np.nan)
print(Alti_H2_Final)


#Mask alti_H2_Final

masked_alti_H2= np.ma.masked_invalid(Alti_H2_Final)


#Hypsometrie

hypsometry, bins = np.histogram(masked_alti_H2.compressed(), bins=bins)

#Area
band_area_h2 = []
for i in hypsometry:
    band_area_h2.append(i * 625)


#Fs_H2

fs_H2 = (BA* 997 * 2442977) / (((parametrication.iloc[:,2] * band_area_h2).sum())* 920)


###############################################################Repeat the code for as many Rears you Wish with a loop#########################

#Create a list of each years updated glacier surface and add the first two runs
Alti_List=[]
Alti_List.append(Alti_H1_Final)
Alti_List.append(Alti_H2_Final)

#Indicate the number of years to project into the future
years=50

for x in range(years-2):

    Alti_List[x+1] = None
    for index in range(len(parametrication)):
        Alti_List[x+1] = np.where(((Alti_List[x] >= (parametrication.iloc[index, 4])) & (Alti_List[x] <= (parametrication.iloc[index, 5]))), Alti_List[x] + fs_H1 * parametrication.iloc[index, 2], Alti_List[x+1])

    Alti_List[x+1] = np.array(Alti_List[x+1], dtype=float)
    Alti_List[x+1] = np.where(Alti_List[x+1] >= edit_glacier_bed_array, Alti_List[x+1], np.nan)
    Alti_List.append(Alti_List[x+1])


    # Mask alti

    masked_alti = np.ma.masked_invalid(Alti_List[x+1])

    # Hypsometrie

    hypsometry, bins = np.histogram(masked_alti.compressed(), bins=bins)

    # Area
    band_area = []
    for i in hypsometry:
        band_area.append(i * 625)

    # Fs_H2

    fs_years = (BA * 997 * 2442977) / (((parametrication.iloc[:, 2] * band_area).sum()) * 920)


#Safe the updated glacier surface

NewFile = ws+'/'+f'gltsf_{2016+years}.tif'
createRasterFromCopy(NewFile, edit_alti3d, Alti_List[years-1])

NewFile=None
Alti_List=None

sum(band_area)

