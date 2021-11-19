

# Imports
from osgeo import osr, gdal, ogr
import numpy as np
import pandas as pd

# Functions

def getRasterBand (ds, band=1, access=0):
    band=ds.GetRasterBand(1).ReadAsArray()
    return band

def createRasterFromCopy(dst,ds,data,driverFmt='GTiff'):
    driver=gdal.GetDriverByName(driverFmt)
    outds=driver.CreateCopy(dst,ds,strict=0)
    outds.GetRasterBand(1).WriteArray(data)
    ds=None
    outds=None

def normalize_DHM(dhm):
    dhm_n = dhm.copy()
    dhm_n = (dhm.max() - dhm)/(dhm.max() - dhm.min())
    return dhm_n
def normalize_dh (dh):
    dh_n = dh.copy()
    dh_n = dh/dh.max()
    return dh_n

# Workspace: Enter the path of a separate workspace for the implementation

ws = input('Enter the path of your workspace for the implementation script:')

#Check Input Data

print('Make sure that all seven input files according to the README are saved in your ws')

#Drivers and Proj(EPSG 21781 for LV03)
drv = gdal.GetDriverByName('GTiff')
srs = osr.SpatialReference()
srs.ImportFromEPSG(21781)


#Glacier to model
glacier = 'Glacier de Tsanfleuron'

#Open and edit files

#Open dhm25
dhm98=gdal.Open(ws + '/dhm25_grid_raster.tif')

#Edit dhm25(Reproject and Clip) with the 1998 glacier extend
ba_edit_dhm98 = gdal.Warp(ws + '/' + 'ba_edit_dhm25.tif', dhm98, dstSRS='EPSG:2056', cutlineDSName=ws + "/98_outline/outline_98_2.shp", cutlineWhere=f"name='{glacier}'", cropToCutline=True, dstNodata=np.nan)

#Open and Edit dhm16 (Resample and Clip) with the 1998 glacier extend
dhm16 = gdal.Open(ws + '/glacier_tsanfleuron.tif')
transform = dhm98.GetGeoTransform()
ba_edit_dhm16 =gdal.Warp(ws + '/ba_edit_glacier_tsanfleuron.tif', dhm16, xRes=transform[1], yRes=transform[1], resampleAlg="bilinear", cutlineDSName=ws + "/98_outline/outline_98_2.shp", cutlineWhere=f"name='{glacier}'", cropToCutline=True, dstNodata=np.nan)

#Open the parametrication .txt file
parametrization = pd.read_csv(ws + '/deltaH_Glacier de Tsanfleuron.txt', sep=';')

#Open the Edit dhm16 file with the 2016 glacier extend
edit_dhm16 = gdal.Open(ws + '/edit_glacier_tsanfleuron.tif')

#Open and edit the glacier bed file
glacier_bed = gdal.Open(ws + '\GlacierBed.tif')
edit_glacier_bed =gdal.Warp(ws +'/glacier_bed_gltsf.tif', glacier_bed, xRes=25, yRes=25, resampleAlg="bilinear", cutlineDSName=ws + "/16_outlines/SGI_2016_glaciers.shp", cutlineWhere=f"name='{glacier}'", cropToCutline=True, dstNodata=np.nan)

#########################################################Calculating Geodetic Mass Balance Change (Ba) according to Fischer M. et al. 2015##############################################


#Calculate volume change from 1998 to 2016

NewFile = ws+'/'+ 'ba_substract_glacier_tsanfleuron.tif'

#Calculate Diffrence and write to a new Tiff

Old=getRasterBand(ba_edit_dhm98)
New=getRasterBand(ba_edit_dhm16)
Diff=Old-New

createRasterFromCopy(NewFile, ba_edit_dhm16, Diff)

ba_substract = gdal.Open(ws+'/'+'ba_substract_glacier_tsanfleuron.tif')

#Read as Array
ba_substractArray = ba_substract.GetRasterBand(1).ReadAsArray()
ba_dhm16Array = ba_edit_dhm16.ReadAsArray()

#Masking the two dhm's

ba_masked_substract= np.ma.masked_invalid(ba_substractArray)
ba_masked_dhm16= np.ma.masked_invalid(ba_dhm16Array)

#Merge the two Masks
ba_multimask = np.ma.mask_or(np.ma.getmask(ba_masked_substract), np.ma.getmask(ba_masked_dhm16))

ba_substract_Final_Mask=np.ma.array(ba_substractArray, mask=ba_multimask, fill_value=np.nan ).compressed()
ba_dhm16_Final_Mask=np.ma.array(ba_dhm16Array, mask=ba_multimask, fill_value=np.nan).compressed()

#Make Dataframe dh/DHM
ba_df =  pd.DataFrame(np.column_stack([ba_substract_Final_Mask, ba_dhm16_Final_Mask]), columns=['dh', 'DHM'])
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

#fs= Ba/fs*pice * Sum (Ai* dhi)


#Band Area * normalized elevation range (Ba in m.w.a/yr is convertet in to m with density of water (997) and the area.


fs= (BA* 997 * 2442977) / (((parametrization.iloc[:, 2] * parametrization.iloc[:, 6]).sum()) * 920)

##############################################################Calculate h1################################################################################################


#Read the alti3d file with 2016 glacier extend and the glacier bed file as an array

dhm16Array = edit_dhm16.ReadAsArray()
edit_glacier_bed_array = edit_glacier_bed.ReadAsArray()


#####Update alti 3d array band by band with dh and compare with glacier bed!!!!!

Alti_H1 = None
for index in range(len(parametrization)):
    if index == 0:
        Alti_H1 = np.where(((dhm16Array >= (parametrization.iloc[index, 4])) & (dhm16Array <= (parametrization.iloc[index, 5]))), dhm16Array + fs * parametrization.iloc[index, 2], dhm16Array)

    else:
        Alti_H1 = np.where(((dhm16Array >= (parametrization.iloc[index, 4])) & (dhm16Array <= (parametrization.iloc[index, 5]))), dhm16Array + fs * parametrization.iloc[index, 2], Alti_H1)

Alti_H1_Final = np.where(Alti_H1 >= edit_glacier_bed_array, Alti_H1, np.nan)



########################################################Calculae new fs_H1 according to alti_H1_final#########################################################################

#Mask alti_H1_Final

masked_alti_H1= np.ma.masked_invalid(Alti_H1_Final)

#Elevation Bands
bins = list (parametrization.iloc[:, 4])

bins.append(parametrization.iloc[-1, 5])

#Hypsometry

hypsometry, bins = np.histogram(masked_alti_H1.compressed(), bins=bins)

#Area
band_area_h1 = []
for i in hypsometry:
    band_area_h1.append(i * 625)

#Fs_H1

fs_H1 = (BA* 997 * 2442977) / (((parametrization.iloc[:, 2] * band_area_h1).sum()) * 920)

#Calculate Alti_H2 with fs_H1
Alti_H2 = None
for index in range(len(parametrization)):

    Alti_H2 = np.where(((Alti_H1_Final >= (parametrization.iloc[index, 4])) & (Alti_H1_Final <= (parametrization.iloc[index, 5]))), Alti_H1_Final + fs_H1 * parametrization.iloc[index, 2], Alti_H2)

Alti_H2_float = np.array(Alti_H2, dtype= float)
Alti_H2_Final = np.where(Alti_H2_float >= edit_glacier_bed_array, Alti_H2_float, np.nan)


#########################################Calculate fs_H2 according to alti_H2################################################################
#Mask alti_H2_Final

masked_alti_H2= np.ma.masked_invalid(Alti_H2_Final)


#Hypsometrie

hypsometry, bins = np.histogram(masked_alti_H2.compressed(), bins=bins)

#Area
band_area_h2 = []
for i in hypsometry:
    band_area_h2.append(i * 625)


#Fs_H2

fs_H2 = (BA* 997 * 2442977) / (((parametrization.iloc[:, 2] * band_area_h2).sum()) * 920)


###############################################################Repeat the code for as many years you like with a loop#########################

#Create a list of each years updated glacier surface and add the first two runs
Alti_List=[]
Alti_List.append(Alti_H1_Final)
Alti_List.append(Alti_H2_Final)

#Indicate the number of years to project into the future
years= int(input ('number of years you want to model in to the future:'))

#Run the loop for as many years as insertet

for x in range(years-2):

    Alti_List[x+1] = None
    for index in range(len(parametrization)):
        Alti_List[x+1] = np.where(((Alti_List[x] >= (parametrization.iloc[index, 4])) & (Alti_List[x] <= (parametrization.iloc[index, 5]))), Alti_List[x] + fs_H1 * parametrization.iloc[index, 2], Alti_List[x + 1])

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

    fs_years = (BA * 997 * 2442977) / (((parametrization.iloc[:, 2] * band_area).sum()) * 920)

#Safe the updated glacier surface to ws

NewFile = ws+'/'+f'gltsf_{2016+years}.tif'
createRasterFromCopy(NewFile, edit_dhm16, Alti_List[years - 1])

NewFile=None

print('you will find a .tif file: gltsf_... with the year number according to your insertet number of years in your ws ')

#Calculating the difference in glacier surface elevation between 2016 and the year you have chosen
substract_years = dhm16Array - Alti_List[years - 1]
NewFile = ws+'/'+f'substract_gltsf_2016-{2016+years}.tif'
createRasterFromCopy(NewFile, edit_dhm16, substract_years)

Alti_List=NewFile=None

print('you will find a .tif file: substract_gltsf_2016-(the year you have chosen) in your ws')
print( 'if you like to model another time span just run the code again')

################################################################END#########################################################################