import numpy as np
import math
import matplotlib.pyplot as plt

#****************************************************
#functions
#****************************************************
def gridasciitonumpyarrayfloat(ingridfilefullpath):
    #this function reads a GRID-ASCII raster into a floating point numpy array
    #input is the full path to an ASCCI GRID file
    #output is the float numpy array, the number of columns, the number of rows, the x-coordinate of the lower left corner, y-coordinate of lower left corner, cellsize, NODATA value, and the full string of the ASCII GRID header
    i=0
    row=0
    headerstr=''
    infile=open(ingridfilefullpath, "r")
    for line in infile:
        if i==0:
            ncols=int(line.strip().split()[-1])
            headerstr+=line
        elif i==1:
            nrows=int(line.strip().split()[-1])
            headerstr += line
        elif i==2:
            xllcorner=float(line.strip().split()[-1])
            headerstr += line
        elif i==3:
            yllcorner=float(line.strip().split()[-1])
            headerstr += line
        elif i==4:
            cellsize=float(line.strip().split()[-1])
            headerstr += line
        elif i==5:
            NODATA_value=float(line.strip().split()[-1])
            arr=np.zeros((nrows, ncols), dtype=float)
            arr[:,:]=NODATA_value
            headerstr += line.replace("\n","")
        elif i > 5:
            col = 0
            while col < ncols:
                for item in line.strip().split():
                    arr[row, col] = float(item)
                    col += 1
            row += 1
        i += 1
    infile.close()
    return arr, ncols, nrows, xllcorner, yllcorner, cellsize, NODATA_value, headerstr
def gridasciitonumpyarrayint(ingridfilefullpath):
    #this function reads a GRID-ASCII raster into a floating point numpy array
    #input is the full path to an ASCCI GRID file
    #output is the integer numpy array, the number of columns, the number of rows, the x-coordinate of the lower left corner, y-coordinate of lower left corner, cellsize, NODATA value, and the full string of the ASCII GRID header
    i=0
    row = 0
    headerstr=''
    infile=open(ingridfilefullpath, "r")
    for line in infile:
        if i==0:
            ncols=int(line.strip().split()[-1])
            headerstr+=line
        elif i==1:
            nrows=int(line.strip().split()[-1])
            headerstr += line
        elif i==2:
            xllcorner=float(line.strip().split()[-1])
            headerstr += line
        elif i==3:
            yllcorner=float(line.strip().split()[-1])
            headerstr += line
        elif i==4:
            cellsize=float(line.strip().split()[-1])
            headerstr += line
        elif i==5:
            NODATA_value=float(line.strip().split()[-1])
            arr=np.zeros((nrows, ncols), dtype=int)
            arr[:,:]=NODATA_value
            headerstr += line.replace("\n","")
        elif i>5:
            col=0
            while col<ncols:
                for item in line.strip().split():
                    arr[row,col]=float(item)
                    col+=1
            row+=1
        i+=1
    infile.close()
    return arr, ncols, nrows, xllcorner, yllcorner, cellsize, NODATA_value, headerstr

#****************************************************
# end functions
#****************************************************


#**************************************************************************
#ENVIRONMENT variables - set workspace and names of input files
#**************************************************************************
#set environment and workspace
myworkspace = "C:/Users/jonas/Desktop" #change this to the directory you downloaded and extracted the input data
print("Workspace: " + myworkspace)

#read the input rasters: dem = digital elevation model, startarr=raster with starting points (cells) for rockfall
dem=gridasciitonumpyarrayfloat(myworkspace+"/"+"dhm25_grid_raster.asc")
demarr=dem[0]
demcols=dem[1]
demrows=dem[2]
cellsize=dem[5]
headerstr=dem[7]
plt.imshow(demarr)
print("raster dimension: "+str(demcols)+ "columns and "+ str(demrows)+" rows")