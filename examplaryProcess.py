'''
This is an exemplary chain of subprocesses, used to test modules for
automated metadata (and especially provenance data) generation at runtime.

This example uses a polygonal vector dataset and a raster dataset (landcover) 
as input. The vector data gets reprojected into the CRS of the raster, then 
the amount of different rasterpixels get counted per polygon.
'''

# to use the proj.db the environmental variable PROJ_LIB needs to be
# pointed to the folder where proj.db is stored
# in my case: '.../conda-environment'/Library/share/proj
import geopandas
import rasterio
import rasterstats
import fiona



import numpy as np

import os



def reprojectVec(sourcePath, targetCrs, targetPath):
	# input: sourceLayer: layer with srs to be reprojected
	#		 targetCrs: target srs
	# output: reprojected sourceLayer as shape-file
	sourceDf = geopandas.read_file(sourcePath)
	sourceDf = sourceDf.to_crs(targetCrs)
	sourceDf.to_file(targetPath)

def appendZonalHistograms(vectorPath, rasterPath, targetPath):
	""" This function takes a polygonal vector datasource and a categorical raster as inputs.
	For each polygon the unique values get counted and then as new column appended to the 
	corresponding polygon. """
	gdf = geopandas.read_file(vectorPath)
	
	uniquePixelVals = []
	polyDict = {}
	for line, polygon in enumerate(gdf['geometry']):
		zonalHistograms = rasterstats.zonal_stats(polygon, rasterPath, categorical=True)
		polyDict[line] = zonalHistograms[0]
		for key, val in zonalHistograms[0].items():
			uniquePixelVals.append(key)
	
	uniquePixelVals = list(set(uniquePixelVals))
	for val in uniquePixelVals:
		gdf['class-'+str(val)] = 0

	for line, histograms in polyDict.items():		
		for key, val in histograms.items():			
			colName = 'class-' + str(key)
			gdf.at[line, colName] = val
	gdf.to_file(targetPath)

# define temp location
tempPath = './temp/reprojectedLayer.shp'
# source location
sourcePath = r'C:\Users\arue\Projects\PythonPlayground\ProvEnginePrototype\input\saxony_NUTS\saxony_NUTS.shp'
# get crs from raster
rasterPath = r'C:\Users\arue\Projects\PythonPlayground\ProvEnginePrototype\input\CorineLandCover_Raster\g100_clc12_V18_5.tif'
# define output location
targetPath = r'C:\Users\arue\Projects\PythonPlayground\ProvEnginePrototype\output\out.shp'

with rasterio.open(rasterPath) as raster:
	rasterCrs = raster.crs
reprojectVec(sourcePath = sourcePath, targetCrs = rasterCrs, targetPath = tempPath)
appendZonalHistograms(tempPath, rasterPath, targetPath)

