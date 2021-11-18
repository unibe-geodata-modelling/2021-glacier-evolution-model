#Delta-H Parametrization
#!!!!!Pleas do not Change the code. Have still to order everything!!!!


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
#Workspace
ws = 'C:/Users/jonas/Desktop/workspace/'

NewFile = ws+'/'+'Substract.tif'
Diff=gdal.Open(NewFile)
Alti3D=gdal.Open(ws+'/glacier_tsanfleuron_Edit.tif')

#Read as Array
DiffArray=Diff.GetRasterBand(1).ReadAsArray()
Alti3DArray=Alti3D.ReadAsArray()


#nodata_Diff=Diff.GetRasterBand(1).GetNoDataValue()
#nodata_Alti3D=Alti3D.GetRasterBand(1).GetNoDataValue()

masked_Diff= np.ma.masked_invalid(DiffArray)
masked_Alti3D= np.ma.masked_invalid(Alti3DArray)


hypsometry, bins = np.histogram(masked_Alti3D.compressed(), bins="fd")


#Merge the two Masks
multimask = np.ma.mask_or(np.ma.getmask(masked_Diff), np.ma.getmask(masked_Alti3D))

Diff_Final_Mask=np.ma.array(DiffArray, mask=multimask, fill_value=np.nan ).compressed()
Alti3D_Final_Mask=np.ma.array(Alti3DArray, mask=multimask,fill_value=np.nan).compressed()

#Make Dataframe dh/DEM
glacier_tsanfleuron =  pd.DataFrame(np.column_stack([Diff_Final_Mask, Alti3D_Final_Mask]), columns=['dh','DEM'])

#Make Elevation Bands
glacier_tsanfleuron_sort = glacier_tsanfleuron.sort_values('DEM')
ind = np.digitize(glacier_tsanfleuron_sort['DEM'], bins)

glacier_tsanfleuron_band=glacier_tsanfleuron_sort.groupby(ind).mean()



#Separating dh and DEM
dem_glacier_tsanfleuron = glacier_tsanfleuron_band['DEM']
dh_glacier_tsandfleuron = glacier_tsanfleuron_band['dh']

plt.plot(dem_glacier_tsanfleuron,dh_glacier_tsandfleuron)

#smoth
dem_smoth_glacier_tsanfleuron = dem_glacier_tsanfleuron.rolling(window=3, min_periods=1).mean()
dh_smoth_glacier_tsandfleuron = dh_glacier_tsandfleuron.rolling(window=3, min_periods=1).mean()

plt.plot(dem_smoth_glacier_tsanfleuron, dh_smoth_glacier_tsandfleuron)




#Normalize
def normalize_DEM(dem):
    dem_n = dem.copy()
    dem_n = (dem.max() - dem)/(dem.max() - dem.min())
    return dem_n
def normalize_dh (dh):
    dh_n = dh.copy()
    dh_n = dh/dh.max()
    return dh_n


dem_smoth_glacier_tsanfleuron_n = normalize_DEM(dem_smoth_glacier_tsanfleuron)
dh_smoth_glacier_tsandfleuron_n = normalize_dh(dh_smoth_glacier_tsandfleuron)



#plot and invert DEM with [::-1]

plt.plot(dem_smoth_glacier_tsanfleuron_n, dh_smoth_glacier_tsandfleuron_n)
plt.gca().invert_yaxis()
plt.title('delta-H GLTSF')
plt.xlabel('Normalized elevation range')
plt.ylabel('Normalized ice thickness change')

#Save Plot
plt.savefig(ws+'/delta_H GLTSF.png')

#Save Files as txt

## normalized elevation range, normalized ice tickness change

delta_h_GLTSF_xy_norm = pd.DataFrame( np.column_stack([dem_smoth_glacier_tsanfleuron_n ,dh_smoth_glacier_tsandfleuron_n]), columns=['Normalized elevation range','Normalized ice thickness change'])

np.savetxt(ws+'/deltH_GLTSF_xy_norm.txt', delta_h_GLTSF_xy_norm, delimiter = ';', fmt= '%.5f', header='Normalized elevation range ; Normalized ice thickness change')

## elevation Bands, normalized ice tickness change

delta_h_GLTSF_y_norm = pd.DataFrame( np.column_stack([dem_smoth_glacier_tsanfleuron,dh_smoth_glacier_tsandfleuron_n]), columns=['Elevation Band','Normalized ice thickness change'])

np.savetxt(ws+'/deltH_GLTSF_y_norm.txt', delta_h_GLTSF_y_norm, delimiter = ';', fmt= '%.5f', header='Elevation Band ; Normalized ice thickhess change')

## elevation Bands, ice tickness change

delta_h_GLTSF = pd.DataFrame( np.column_stack([dem_smoth_glacier_tsanfleuron,dh_smoth_glacier_tsandfleuron]), columns=['Elevation Band','Ice thickness change'])

np.savetxt(ws+'/deltH_GLTSF.txt', delta_h_GLTSF, delimiter = ';', fmt= '%.5f', header='Elevation Band ; Ice thickness change')


