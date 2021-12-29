# 2021-glacier-evolution-model

This is the README for the 2021-glacier-evolution-model repository. It contains two scripts. Delta-H Parameterization and the built on it Delta-H Implementation.

## Software

Both skripts were written in Python 3.9. in the PyCharm 2020.3.3 Community Edition.

## Delta-H Parameterization

This script includes the code for parameterizing individual glaciers according to Huss et al. 2010.
Data used to run the script can be downloaded an preprocessed by your self or downloaded via a google drive folder where no preprocessing via GIS is neccesarry. To get access send a mail to jonas.schild@students.unibe.ch. With this script you can do the parameterization for all glaciers included in the Swiss Glacier Inventory 2016.

### Input data

Here a list of the required input data, which has to be saved in to your workspace folder:

  - dhm25_grid_raster.asc -> this is the old digital elevation model of whole switzerland recorded 1998. Available and provided by: https://www.swisstopo.admin.ch/de/geodata/height/dhm25.html
  
  - glacier_tsanfleuron.tif -> this is the modern alti3D digital elevation model recorded 2016. Available and provided by: https://www.swisstopo.admin.ch/de/geodata/height/alti3d.html
                              
                              Because of the larger data amount it is not availble for whole Switzerland. You can just download single squares, which you then have to merge.
                              This is an example for Glacier de Tsanfleuron. 
  
  - 16_outlines -> this is a folder with the glacier outlines of switzerland in 2016. Provided by Swiss Glacier Inventory 2016.

 
All steps to run the script are mentioned in the script it self. Just download the mentioned data above. In the google drive folder is the glacier_tsanfleuron.tif data as an example. If you want to run the scrip for an other glacier just download the matching squares of the Swiss Topo Alti3D via the link above and merge them via QGIS. Then you just have to enter a diffrent file name and glacier name. But this script works for any glacier included in the Swiss Glacier Inventory 2016. 
 
 ### Output data
 
 Here a list of the output data:
 
  - dhm25_grid_raster.tif -> this is the convertet dhm25_grid_raster as gtiff. You will need this for the implementation script.
  - edit_glacier_tsanfleuron.tif -> Alti3D elevation model of 2016 clipt to the 2016 glacier extend. With an upscaled resolution of 25m. You will need this in the                                                   implementation script.
  - edit_dhm25.tif -> Elevation model of 1998 clipt to the 2016 glacier extend. Reprojected from CH1903/LV03 to CH1903+/LV95. 
  - substract_glacier_tsanfleuon.tif -> this is the difference in glacier thickness between 1998 and 2016.
  - a PNG plot of the parametrication
  - a .txt file with the parametrication data-frame ready to run the Delta-H Implemention script -> includes: 

          normalized_elevation_range ; band_elevation ; normalized_ice_thickness_change  ; ice_thickness_change; low_lim; up_lim ; band_area                                                                                                                           
                                                         

## Delta-H Implementation

This script has two parts. First is the calculation of the geodetic massbalance (Ba) according to Fischer et al. 2015. Second ist the glacier evolution model according to Huss et al. 2010. The geodetic massbalance is necessery to solve Eq. 2 of Huss et al. 2010. This Script will work just for the Glacier de Tsanfleuron. For running the script with any swiss glacier the older glacier-outlines dated the same as the dhm25 record of all swiss glaciers would be necessary. 

### Input Data

Make a new workspace folder and add the data below. 
Required input data: 

  - dhm25_grid_raster.tif -> you can copy this from the parametrization ws 
  - glacier_tsanfleuron.tif -> you can copy this from the parametrization ws.
  - edit_glacier_tsanfleuron.tif -> you can copy this from the parametrization ws. 
  - 98_outline -> this folder contains a shape_file of the glacier outline of the year 1998. Drawn according to the ortophoto and the historical Map of 1998. Provided by                           Swisstopo. You have this file in the google drive folder.
  - 16_outlines -> this folder you can copy from the parametrization ws. 
  - GlacierBed.tif -> This is an elevation model of all glacier beds of the Swiss Alps. Provided by ETH Zürich. You find this file in the google drive folder. 
  - deltaH_Glacier de Tsanfleuron.txt -> This is the .txt file of the parametrization. You can copy this from the parametrization ws.

All further steps are  mentioned in the script. The only two things you have to do is to make a workspace folder with the seven files from above and indicate the path of it. A second thing is to enter the number of years you want to project in to the future. 

### Output data

Beside some irrelevant files you will get as an output in your workspace folder these two important files:

  - gltsf_(year according to the insertet number of years).tif -> this is the updated glacier surface for the chosen year.
  - substract_gltsf_2016-(year according to the insertet number of years).tif -> this is the difference of glacier surface elevation between 2016 and your chosen year. 



## Contact

Jonas Schild: jonas.schild@students.unibe.ch
Ann Christine Kogel: ann.kogel@students.unibe.ch
