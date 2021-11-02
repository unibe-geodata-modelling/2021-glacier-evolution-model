# 2021-glacier-evolution-model

This is the instruction for the 2021-glacier-evolution-model repository. It contains two scripts. Delta-H Parametrication and the built on it Delta-H Implementation.

# Delta-H Parametrication

This Script includes the code for parametricing individual glaciers acording to Huss et al. 2010.
Data used to run the script can be downloaded an preprocessed by your self or downloaded via a google drive folder where no preprocessing is neccesarry. To get access send me a mail to jonas.schild@students.unibe.ch

Here a list of the required input data:

  - dhm25_grid_raster.asc -> this is the old digital elevation model of whole switzerland recorded 1998. Available and provided by: https://www.swisstopo.admin.ch/de/geodata/height/dhm25.html
  
  - glacier_tsanfleuron.tif -> this is the modern alti3D digital elevation model recorded 2016. Available and provided by: https://www.swisstopo.admin.ch/de/geodata/height/alti3d.html
                              
                              Because of the larger data amount it is not availble for whole Switzerland. You can just download single squares, which you then have to merge.
                              This is an example for Glacier de Tsanfleuron. 
  
  - glacier_outlines -> this is a folder with the glacier outlines of switzerland in 2016. Provided by Swiss Glacier Inventory 2016
 
All steps to run the script are mentioned in the script self. Just download the mentioned above data. In the google drive folder is the glacier_tsanfleuron.tif data as an example. If you want to run the scrip for an other glacier just downlad the needed squares of the alti3D via the link above and merge them via QGIS. Then you just have to enter a diffrent file name and glacier name. But then this script works for any glacier included in the Swiss Glacier Inventory 2016. 
 
 Here a list of the important output data:
 
  - substract_glacier_tsanfleuon.tif -> this is the difference in glacier thickness between 1998 and 2016.
  - a PNG plot of the parametrication
  - a .txt file with the parametrication data frame ready to run the Delta-H Implemention Script -> includes: 

          normalized_elevation_range ; band_elevation ; normalized_ice_thickness_change  ; ice_thickness_change; low_lim; up_lim ; band_area                                                                                                                           
                                                         

# Delta-H Implementation


