import os, sys, shutil
from osgeo import ogr, osr, gdal
from osgeo.gdalconst import *
gdal.PushErrorHandler('CPLQuietErrorHandler')
import numpy as np
import csv

from metadata import *

class Preprocessing:
	def __init__(self):
		# self.__VECTOR_EXTENSIONS = ['shp', 'gpg']
		# self.__RASTER_EXTENSIONS = ['tif', 'geotiff']
		self.__vecFileExt = '.shp'
		self.__driverName = 'ESRI Shapefile'
		self.__accumulationAreas = []
		self.__targetEpsgCode = 3035
		self.metadata = Metadata()

	def initFileExtensions(self, \
			vecExtension = '.shp', \
			driverName = 'ESRI Shapefile'):
		self.__vecFileExt = vecExtension
		self.__driverName = driverName

	def __cleanup(self):
		# input: workspace path
		#
		# cleans up the temp folder
		print('Cleaning up temp ...')
		for file in os.listdir(self.__workspace + '/temp'):
			print(' remove ' + file)
			os.remove(self.__workspace + '/temp/' + file)


	def initWorkspace(self, workspace):
		self.__workspace = workspace
		self.__savingPath = self.__workspace + '/interimResults/preprocessing/'
		if not os.path.exists(os.path.dirname(self.__savingPath)):
			os.makedirs(self.__savingPath)
		if os.path.exists(os.path.dirname(workspace + '/interimResults/figures/')):
			shutil.rmtree(self.__workspace + '/interimResults/figures/')
		os.makedirs(workspace + '/interimResults/figures/')
		if not os.path.exists(os.path.dirname(workspace + '/temp/')):
			os.makedirs(workspace + '/temp/')
		self.__metadata.initWorkspace(self.__workspace)
		self.__metadata.initSavingPath(self.__workspace + '/interimResults')
				

	def initTargetEpsgCode(self, targetEpsgCode):
		self.__targetEpsgCode = targetEpsgCode

	def __reprojectVec(self, sourceLayer, targetPrj, targetPath):
		# input: sourceLayer: layer with srs to be reprojected
		#		 targetCrs: target srs
		# output: reprojected sourceLayer as shape-file

		driver = ogr.GetDriverByName(self.__driverName)

		sourcePrj = sourceLayer.GetSpatialRef()
		#create transformation
		transform = osr.CoordinateTransformation(sourcePrj, targetPrj)
		
		# create the output layer
		if os.path.exists(targetPath):
			driver.DeleteDataSource(targetPath)
		outDataSource = driver.CreateDataSource(targetPath)
		outLayer = outDataSource.CreateLayer("",targetPrj)

		# add fields
		sourceLayerDefn = sourceLayer.GetLayerDefn()
		for i in range(0, sourceLayerDefn.GetFieldCount()):
			fieldDefn = sourceLayerDefn.GetFieldDefn(i)
			outLayer.CreateField(fieldDefn)

		# get the output layer's feature definition
		outLayerDefn = outLayer.GetLayerDefn()

		#loop through features and transform them
		for feature in sourceLayer:
			# get the input geometry
			geom = feature.GetGeometryRef()
			# reproject the geometry
			geom.Transform(transform)
			# create a new feature
			outFeature = ogr.Feature(outLayerDefn)
			# set the geometry and attribute
			outFeature.SetGeometry(geom)
			for i in range(0, outLayerDefn.GetFieldCount()):
				outFeature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(), feature.GetField(i))
			# add the feature to the shapefile
			outLayer.CreateFeature(outFeature)
			# dereference the features and get the next input feature
			outFeature = None

		# close data source
		outDataSource.Destroy()

	def initShape(self, path):
		# defines shape of model area, transforms to target crs if necessary
		# give as vector file with target shape as single or first feature
		# copies shape in interim folder

		# define saving location
		newPath = self.__savingPath + 'shape/'
		if not os.path.exists(os.path.dirname(newPath)):
			os.makedirs(newPath)
		self.__shapePath = newPath + 'shape' + self.__vecFileExt

		# load shape
		shapeSource = ogr.Open(path,1)
		shapeLayer = shapeSource.GetLayer(0)
		shapeCrs = shapeLayer.GetSpatialRef()
		
		targetSpatialReference = osr.SpatialReference()
		targetSpatialReference.ImportFromEPSG(self.__targetEpsgCode)


		if (shapeCrs.ExportToProj4() != targetSpatialReference.ExportToProj4()):
			self.__reprojectVec(\
				sourceLayer = shapeLayer,\
				targetPrj = targetSpatialReference,\
				targetPath = self.__shapePath)
		else:
			driver = ogr.GetDriverByName(self.__driverName)
			if os.path.exists(self.__shapePath):
				driver.DeleteDataSource(self.__shapePath)
			outDataSource = driver.CreateDataSource(self.__shapePath)
			outLayer = outDataSource.CopyLayer(shapeLayer,'')
			outDataSource.Destroy()

		print('Shape path is: ' + self.__shapePath)
		shapeSource.Destroy()

		#self.__metadata.appendInput(path = self.__shapePath)


	def initGrid(self, path):
		# same funtionality as initShape

		# set output path
		newPath = self.__savingPath + 'grid/'
		if not os.path.exists(os.path.dirname(newPath)):
			os.makedirs(newPath)
		self.__gridPath = newPath + 'grid' + self.__vecFileExt

		# load grid
		gridSource = ogr.Open(path,1)
		gridLayer = gridSource.GetLayer(0)
		gridCrs = gridLayer.GetSpatialRef()
		
		targetSpatialReference = osr.SpatialReference()
		targetSpatialReference.ImportFromEPSG(self.__targetEpsgCode)


		if (gridCrs.ExportToProj4() != targetSpatialReference.ExportToProj4()):
			self.__reprojectVec(\
				sourceLayer = gridLayer,\
				targetPrj = targetSpatialReference,\
				targetPath = self.__gridPath)
		else:
			driver = ogr.GetDriverByName(self.__driverName)
			if os.path.exists(self.__gridPath):
				driver.DeleteDataSource(self.__gridPath)
			outDataSource = driver.CreateDataSource(self.__gridPath)
			outLayer = outDataSource.CopyLayer(gridLayer,'')
			outDataSource.Destroy()


		print('Grid Path is: ' + self.__gridPath)
		gridSource.Destroy()
		self.__clipGridToShape()
		self.__accumulationAreas.append(self.__gridPath)

	def __addFieldInt(self, name, layer):
		# create field if not existend
		# (GetFieldIndex retrun -1 if no field with 'name' is found)
		layer_def = layer.GetLayerDefn()
		if layer_def.GetFieldIndex(name) == -1:
			field_def = ogr.FieldDefn(name, ogr.OFTInteger)
			layer.CreateField(field_def)

		layer_def = layer.GetLayerDefn()
		fieldIndex = layer_def.GetFieldIndex(name)
		return (layer, fieldIndex)

	def __addFieldReal(self, name, layer):
		# create field if not existend
		# (GetFieldIndex retrun -1 if no field with 'name' is found)
		layer_def = layer.GetLayerDefn()
		if layer_def.GetFieldIndex(name) == -1:
			field_def = ogr.FieldDefn(name, ogr.OFTReal)
			layer.CreateField(field_def)

		layer_def = layer.GetLayerDefn()
		fieldIndex = layer_def.GetFieldIndex(name)
		return (layer, fieldIndex)

	def __addFieldString(self, name, layer):
		# create field if not existend
		# (GetFieldIndex retrun -1 if no field with 'name' is found)
		layer_def = layer.GetLayerDefn()
		if layer_def.GetFieldIndex(name) == -1:
			field_def = ogr.FieldDefn(name, ogr.OFTString)
			layer.CreateField(field_def)

		layer_def = layer.GetLayerDefn()
		fieldIndex = layer_def.GetFieldIndex(name)
		return (layer, fieldIndex)

	def __readCsvAsShp(self, sourcePath, targetPath, driverName, id, target, \
			horizontalCoord, verticalCoord, epsgCode, delimiter = ',' , additionalKeeps = []):
		# base code with minor changes from:
		# http://www.digital-geography.com/csv-to-shp-with-python/

		# input: path to csv file
		# 		 path to storing place of shp file
		# 		 list of variables from csv wich shall be kept in attribute table
		#		 horizontalCoord, name of x-value of coordinate in csv file
		#		 verticalCoord, name of y-value of coordinate in csv file
		#		 epsg code of sorce srs
		# 		 delimiter of source file

		# converts target csv file with geoinformation to shapefile. ALL FIELDNAMES IN SOURCE CSV 
		# FILE HAVE TO BE LOWER THEN 10 CARACTERS! (due to shapefile limitations)

		spatialReference = osr.SpatialReference() #will create a spatial reference locally to tell the system what the reference will be
		spatialReference.ImportFromEPSG(int(epsgCode)) #here we define this reference to be the EPSG code
		driver = ogr.GetDriverByName(driverName) # will select the driver for our shp-file creation.
		if os.path.exists(targetPath):
			driver.DeleteDataSource(targetPath)
		shapeData = driver.CreateDataSource(targetPath) #so there we will store our data
		layer = shapeData.CreateLayer('', spatialReference, ogr.wkbPoint) #this will create a corresponding layer for our data with given spatial information.
		layer_defn = layer.GetLayerDefn() # gets parameters of the current shapefile
		index = 0
		keepFields = [id, target]
		for keep in additionalKeeps:
			keepFields.append(keep)
		with open(sourcePath, 'rt') as csvfile:
			readerDict = csv.DictReader(csvfile, delimiter=delimiter)
			for field in keepFields:
				#we will create a new field if it is inside keep
				new_field = ogr.FieldDefn(field, ogr.OFTString)
				layer.CreateField(new_field)
			for row in readerDict:
				#print(row)
				point = ogr.Geometry(ogr.wkbPoint)
				point.AddPoint(float(row[horizontalCoord]),float(row[verticalCoord])) 
				# we do have horizontalCoord and verticalCoord as Strings, so we convert them
				feature = ogr.Feature(layer_defn)
				feature.SetGeometry(point) #set the coordinates
				feature.SetFID(index)
				for field in keepFields:
					i = feature.GetFieldIndex(field)
					# print(row[field])
					# print(type(row[field]))
					feature.SetField(i, row[field])
				layer.CreateFeature(feature)
				index += 1
		shapeData.Destroy()
		return readerDict.fieldnames


	def __createBuffer(self, pathToInput, pathToOutput, bufferDist, driverName):
		# with minor changes taken from 
		# https://pcjericks.github.io/py-gdalogr-cookbook/vector_layers.html
		
		inputds = ogr.Open(pathToInput)
		inputlyr = inputds.GetLayer()

		fieldnames = []
		ldefn = inputlyr.GetLayerDefn()
		for n in range(ldefn.GetFieldCount()):
			fdefn = ldefn.GetFieldDefn(n)
			fieldnames.append(fdefn.name)		


		spatialReference = inputlyr.GetSpatialRef()	
		shpdriver = ogr.GetDriverByName(driverName)
		if os.path.exists(pathToOutput):
			shpdriver.DeleteDataSource(pathToOutput)
		outputBufferds = shpdriver.CreateDataSource(pathToOutput)
		bufferlyr = outputBufferds.CreateLayer(pathToOutput, spatialReference, geom_type=ogr.wkbPolygon)
		featureDefn = bufferlyr.GetLayerDefn()

		# add fieldnames of point layer to new layer
		for name in fieldnames:
			self.__addFieldString(name, bufferlyr)

		print(' ' + str(bufferDist))
		for feature in inputlyr:
			ingeom = feature.GetGeometryRef()
			geomBuffer = ingeom.Buffer(bufferDist)

			outFeature = ogr.Feature(featureDefn)
			outFeature.SetGeometry(geomBuffer)
			bufferlyr.CreateFeature(outFeature)
			for name in fieldnames:
				fieldValue = feature.GetField(name)
				fieldIndex = featureDefn.GetFieldIndex(name)
				outFeature.SetField(fieldIndex, fieldValue)
			bufferlyr.SetFeature(outFeature)
			outFeature = None
		outputBufferds.Destroy()


	def initReferenceStations(self, path, horizontalCoordName, verticalCoordName,\
			stationId, targetVariableName, sourceEpsg, delimiter=',', radii = [2000], additionalFields = []):
		# create reference stations point layer (readCsvAsShp), reprojects to target Crs
		# constructs buffers as accumulation zones for predictors with given radii arround those points

		newpath = self.__savingPath + 'referenceStationsSource/'
		if not os.path.exists(os.path.dirname(newpath)):
			os.makedirs(newpath)
		self.__referenceStationsPath = newpath + 'referenceStationsSource' + self.__vecFileExt

		self.__readCsvAsShp (\
			sourcePath = path,\
			targetPath = self.__referenceStationsPath,\
			driverName = self.__driverName,\
			id = stationId,\
			target = targetVariableName,\
			horizontalCoord = horizontalCoordName,\
			verticalCoord = verticalCoordName,\
			epsgCode = sourceEpsg,\
			delimiter = delimiter,\
			additionalKeeps = additionalFields)

		print('Reference stations path is: ' + self.__referenceStationsPath)

		# load reference stations layer
		referenceStationsSource = ogr.Open(self.__referenceStationsPath)
		referenceStationsLayer = referenceStationsSource.GetLayer(0)
		referenceStationsCrs = referenceStationsLayer.GetSpatialRef()

		# load modelling area layer
		modelAreaSource = ogr.Open(self.__shapePath)
		modelAreaLayer = modelAreaSource.GetLayer(0)
		modelAreaCrs = modelAreaLayer.GetSpatialRef()

		# load spatial ref
		targetSpatialReference = osr.SpatialReference()
		targetSpatialReference.ImportFromEPSG(self.__targetEpsgCode)

		# reproject stations to crs of layer model area, if not allready in the same projection
		if (referenceStationsCrs.ExportToProj4() != targetSpatialReference.ExportToProj4()):
			self.__reprojectVec(\
				sourceLayer = referenceStationsLayer,\
				targetPrj = targetSpatialReference,\
				targetPath = self.__referenceStationsPath)
			print('Reprojecting reference stations ...')
			referenceStationsSource = ogr.Open(self.__referenceStationsPath)
			referenceStationsLayer = referenceStationsSource.GetLayer(0)
			referenceStationsCrs = referenceStationsLayer.GetSpatialRef()

		radius = max(radii)
		# obtain the geomtry of the polygon feature in the layer which describes the
		# modelling arera
		feature = modelAreaLayer.GetNextFeature()
		geom = feature.GetGeometryRef()
		#setup negative buffer with max radius to make sure all bufferd stations are inside area
		newGeom = geom.Buffer(-radius)
		#remove stations outside
		print('Removing stations outside modelling area ...')
		driver = ogr.GetDriverByName(self.__driverName)
		# apply filter
		referenceStationsLayer.SetSpatialFilter(newGeom)
		# save
		if os.path.exists(self.__referenceStationsPath):
			driver.DeleteDataSource(self.__referenceStationsPath)
		outDataSet = driver.CreateDataSource(self.__referenceStationsPath)
		outDataSet.CopyLayer(referenceStationsLayer,'')
		outDataSet.Destroy()

		# create buffers
		print ('Buffering reference stations ...')

		newpath = self.__savingPath + 'bufferedRefStations/'
		if not os.path.exists(os.path.dirname(newpath)):
			os.makedirs(newpath)
		for radius in radii:
			bufferedStationsPath = newpath + 'bufferedRefStations_'	+ str(radius) + self.__vecFileExt
			self.__accumulationAreas.append(bufferedStationsPath)
			self.__createBuffer(self.__referenceStationsPath, bufferedStationsPath, radius, self.__driverName)
		print('Path to buffered stations is: ' + newpath)
		referenceStationsSource.Destroy()
		modelAreaSource.Destroy()
		self.__cleanup()
	

	def __clipGridToShape(self):
		# load refernce grid layer
		refGridSource = ogr.Open(self.__gridPath , 1)
		refGridLayer = refGridSource.GetLayer(0)
		refGridCrs = refGridLayer.GetSpatialRef()

		# load modelling area layer
		modelAreaSource = ogr.Open(self.__shapePath)
		modelAreaLayer = modelAreaSource.GetLayer(0)
		modelAreaCrs = modelAreaLayer.GetSpatialRef()

		# obtain the geomtry of the polygon feature in the layer which describes the
		# modelling area
		feature = modelAreaLayer.GetNextFeature()
		geometry = feature.GetGeometryRef()
		# clip grid by this area
		print('clipping Grid...')
		refGridLayer.SetSpatialFilter(geometry)

		driver = ogr.GetDriverByName(self.__driverName)
		if os.path.exists(self.__gridPath):
			driver.DeleteDataSource(self.__gridPath)
		outDataSource = driver.CreateDataSource(self.__gridPath)
		outLayer = outDataSource.CopyLayer(refGridLayer,'')

		outDataSource.Destroy()
		refGridSource.Destroy()
		modelAreaSource.Destroy()		

			#  alternate way to clip:
			# 	shapeDf = geopandas.read_file(self.__shapePath)
			# 	gridDf = geopandas.read_file(self.__gridPath)

			# 	# take geom of first feature as mask (there is only one feature in this file)
			# 	mask = shapeDf.geometry[0]
				
			# 	# gridDf.geometry.intersects(mask): list with True or False
			# 	gridDf = gridDf[gridDf.geometry.intersects(mask)]
			# 	gridDf = gridDf.reset_index(drop=True)
			# 	# print(gridDf.head())

			# 	newPath = self.__savingPath + '/grid_clipped/'
			# 	if not os.path.exists(os.path.dirname(newPath)):
			# 		os.makedirs(newPath)
			# 	self.__gridPath = newPath + 'grid_clipped' + self.__vecFileExt
			# 	gridDf.to_file(\
			# 		driver = self.__driverName,\
			# 		filename = self.__gridPath)
			# 	print('Clipped grid Path is: ' + self.__gridPath)


	def __bboxToPixelOffsets(self, gt, bbox):
		# input:	gt, geotransform of source layer
		# 			bbox, target bbox
		#
		# function calculates the origin and width/ height for 
		# a new raster layer which matches the bbox, but with 
		# properties of gt
		originX = gt[0]
		originY = gt[3]
		pixel_width = gt[1]
		pixel_height = gt[5]

		# get pixel counts
		x1 = int((bbox[0] - originX) / pixel_width)
		x2 = int((bbox[1] - originX) / pixel_width) + 1

		y1 = int((bbox[3] - originY) / pixel_height)
		y2 = int((bbox[2] - originY) / pixel_height) + 1

		xsize = x2 - x1
		ysize = y2 - y1
		return (x1, y1, xsize, ysize)

	def __zonalHistograms(self, vectorPath, rasterPath, prefix, nodataValue=None, globalSrcExtent=False):
		#script based on:
		"""
		Zonal Statistics
		Vector-Raster Analysis
		Copyright 2013 Matthew Perry
		"""
		#https://gist.github.com/perrygeo/5667173

		# input:	path to vector file
		#			path to raster file
		#			prefix for new attribute fields
		# returns:	list of unique values inside rhe area of the vector file
		#			nestesd dict: {Fid : {unique value : count}}


		rds = gdal.Open(rasterPath, GA_ReadOnly)
		assert(rds)
		rb = rds.GetRasterBand(1)
		rgt = rds.GetGeoTransform()

		if nodataValue:
			nodataValue = float(nodataValue)
			rb.SetNoDataValue(nodataValue)

		vds = ogr.Open(vectorPath,1)  
		assert(vds)
		vlyr = vds.GetLayer(0)

		# create an in-memory numpy array of the source raster data
		# covering the whole extent of the vector layer
		if globalSrcExtent:
			# use global source extent
			# useful only when disk IO or raster scanning inefficiencies are your limiting factor
			# advantage: reads raster data in one pass
			# disadvantage: large vector extents may have big memory requirements
			src_offset = self.__bboxToPixelOffsets(rgt, vlyr.GetExtent())
			src_array = rb.ReadAsArray(*src_offset)

			# calculate new geotransform of the layer subset
			new_gt = (
				(rgt[0] + (src_offset[0] * rgt[1])),
				rgt[1],
				0.0,
				(rgt[3] + (src_offset[1] * rgt[5])),
				0.0,
				rgt[5]
			)

		mem_drv = ogr.GetDriverByName('Memory')
		driver = gdal.GetDriverByName('MEM')

		# Loop through vectors
		uniqueValues = []
		featureHistoDict = {}
		feat = vlyr.GetNextFeature()
		while feat is not None:

			#print(' processing grid cell ' + str(feat.GetFID()))
			if not globalSrcExtent:
				# use local source extent
				# fastest option when you have fast disks and well indexed raster (ie tiled Geotiff)
				# advantage: each feature uses the smallest raster chunk
				# disadvantage: lots of reads on the source raster
				src_offset = self.__bboxToPixelOffsets(rgt, feat.geometry().GetEnvelope())
				src_array = rb.ReadAsArray(*src_offset)

				# calculate new geotransform of the feature subset
				new_gt = (
					(rgt[0] + (src_offset[0] * rgt[1])),
					rgt[1],
					0.0,
					(rgt[3] + (src_offset[1] * rgt[5])),
					0.0,
					rgt[5]
				)

			# Create a temporary vector layer in memory
			mem_ds = mem_drv.CreateDataSource('out')
			mem_layer = mem_ds.CreateLayer('poly', None, ogr.wkbPolygon)
			mem_layer.CreateFeature(feat.Clone())

			# Rasterize it
			rvds = driver.Create('', src_offset[2], src_offset[3], 1, gdal.GDT_Byte)
			rvds.SetGeoTransform(new_gt)
			gdal.RasterizeLayer(rvds, [1], mem_layer, burn_values=[1])
			rv_array = rvds.ReadAsArray()

			# Mask the source data array with our current feature
			# we take the logical_not to flip 0<->1 to get the correct mask effect
			# we also mask out nodata values explictly
			masked = np.ma.MaskedArray(
				src_array,
				mask=np.logical_or(
					src_array == nodataValue,
					np.logical_not(rv_array)
				)
			)
			#count unique values
			unique, counts = np.unique(masked, return_counts=True)
			record = list(zip(unique,counts))[:-1]

			for (value, counts) in record:
				if (value not in uniqueValues):
					uniqueValues.append(value)
			#record.append(('fid',feat.GetFID()))
			featureHistoDict[feat.GetFID()] = dict(record)
			rvds = None
			mem_ds = None
			feat = vlyr.GetNextFeature()

		vds = None
		rds = None
		return np.sort(uniqueValues), featureHistoDict


	def appendCategorialRasterData(self, catRasterPath, prefix, removeFirstColumn = False):
				
		# max prefix lenth = 4 chars!
		# if the rasterizeVectors.py script is used, the first collumn represents pixels which have no 
		# category (value = 0). we might want to lose those. 
		for path in self.__accumulationAreas:
			vecZonesPath = path

			# load model grid
			vecZonesSource = ogr.Open(vecZonesPath,1)
			vecZonesLayer = vecZonesSource.GetLayer(0)
			vecZonesCrs = (vecZonesLayer.GetSpatialRef())

			# load categorial Raster
			catRasterSource = gdal.Open(catRasterPath)
			catRasterCrs = osr.SpatialReference()
			catRasterCrs.ImportFromWkt(catRasterSource.GetProjectionRef())

			targetSpatialReference = osr.SpatialReference()
			targetSpatialReference.ImportFromEPSG(self.__targetEpsgCode)

			# warp raster crs to vecZonesCrs if not the same and save new raster to temp
			if (catRasterCrs.ExportToProj4() != targetSpatialReference.ExportToProj4()):
				print('Performing coordinate transformation on categorial raster...')
				catRasterPath = self.__workspace + '/temp/warpedRaster.tif'
				gdal.Warp(catRasterPath, catRasterSource, dstSRS=targetSpatialReference)
				# reload categorial Raster
				catRasterSource = gdal.Open(catRasterPath)
				catRasterCrs = osr.SpatialReference()
				catRasterCrs.ImportFromWkt(catRasterSource.GetProjectionRef())
				


			# calculate zonal histograms
			print('computing zonal histograms')
			uniqueValues, zonalHistograms = self.__zonalHistograms(vecZonesPath,catRasterPath, prefix)
			if (removeFirstColumn):
				uniqueValues = uniqueValues[1:]

			# add fields for unique values
			print('adding new fields to table')
			for value in uniqueValues:
				currentFieldName = prefix + '-' + str(value)
				vecZonesLayer, current_field_index = self.__addFieldReal(currentFieldName, vecZonesLayer)

			# fill attribute table with count values from zonal histogram or zero if there was 
			# no count data for certain categrory
			print('filling up attribute table')
			vecZonesLayerDefn = vecZonesLayer.GetLayerDefn()
			# loop through features and assign count data
			for feature in vecZonesLayer:
				currentFid = feature.GetFID()
				# first add up all values in unique values to calc normalized field values
				sum = 0
				for value in uniqueValues:
					if value in zonalHistograms[currentFid]:
						sum += zonalHistograms[currentFid][value]
				# loop through new fields
				for value in uniqueValues:
					currentFieldName = prefix + '-' + str(value)
					currentFieldIndex = vecZonesLayerDefn.GetFieldIndex(currentFieldName)
					if value in zonalHistograms[currentFid]:
						feature.SetField(currentFieldIndex, float(zonalHistograms[currentFid][value]/sum))
					else:
						feature.SetField(currentFieldIndex, float(0))
				vecZonesLayer.SetFeature(feature)

			#printVectorLayerInfo(vecZonesLayer)

			vecZonesSource.Destroy()
			catRasterSource = None
		self.__cleanup()

	def __zonalStats(self, vectorPath, rasterPath, nodataValue=None, globalSrcExtent=False):
		"""
		# with marginal changes taken from:
		# https://gist.github.com/perrygeo/5667173

		Zonal Statistics
		Vector-Raster Analysis
		Copyright 2013 Matthew Perry
		"""
		rds = gdal.Open(rasterPath, GA_ReadOnly)
		assert(rds)
		rb = rds.GetRasterBand(1)
		rgt = rds.GetGeoTransform()

		if nodataValue:
			nodataValue = float(nodataValue)
			rb.SetNoDataValue(nodataValue)

		vds = ogr.Open(vectorPath, GA_ReadOnly)  # TODO maybe open update if we want to write stats
		assert(vds)
		vlyr = vds.GetLayer(0)
		# create an in-memory numpy array of the source raster data
		# covering the whole extent of the vector layer
		if globalSrcExtent:
			# use global source extent
			# useful only when disk IO or raster scanning inefficiencies are your limiting factor
			# advantage: reads raster data in one pass
			# disadvantage: large vector extents may have big memory requirements
			src_offset = self.__bboxToPixelOffsets(rgt, vlyr.GetExtent())
			src_array = rb.ReadAsArray(*src_offset)

			# calculate new geotransform of the layer subset
			new_gt = (
				(rgt[0] + (src_offset[0] * rgt[1])),
				rgt[1],
				0.0,
				(rgt[3] + (src_offset[1] * rgt[5])),
				0.0,
				rgt[5]
			)

		mem_drv = ogr.GetDriverByName('Memory')
		driver = gdal.GetDriverByName('MEM')

		# Loop through vectors
		featureStatsDict = {}
		feat = vlyr.GetNextFeature()
		while feat is not None:

			if not globalSrcExtent:
				# use local source extent
				# fastest option when you have fast disks and well indexed raster (ie tiled Geotiff)
				# advantage: each feature uses the smallest raster chunk
				# disadvantage: lots of reads on the source raster
				src_offset = self.__bboxToPixelOffsets(rgt, feat.geometry().GetEnvelope())
				src_array = rb.ReadAsArray(*src_offset)

				# calculate new geotransform of the feature subset
				new_gt = (
					(rgt[0] + (src_offset[0] * rgt[1])),
					rgt[1],
					0.0,
					(rgt[3] + (src_offset[1] * rgt[5])),
					0.0,
					rgt[5]
				)

			# Create a temporary vector layer in memory
			mem_ds = mem_drv.CreateDataSource('out')
			mem_layer = mem_ds.CreateLayer('poly', None, ogr.wkbPolygon)
			mem_layer.CreateFeature(feat.Clone())

			# Rasterize it
			rvds = driver.Create('', (src_offset[2]), (src_offset[3]), 1, gdal.GDT_Byte)
			rvds.SetGeoTransform(new_gt)
			gdal.RasterizeLayer(rvds, [1], mem_layer, burn_values=[1])
			rv_array = rvds.ReadAsArray()

			# Mask the source data array with our current feature
			# we take the logical_not to flip 0<->1 to get the correct mask effect
			# we also mask out nodata values explictly
			masked = np.ma.MaskedArray(
				src_array,
				mask=np.logical_or(
					src_array == nodataValue,
					np.logical_not(rv_array)
				)
			)

			feature_stats = {
				'min': float(masked.min()),
				'mean': float(masked.mean()),
				'max': float(masked.max()),
				'std': float(masked.std()),
				'sum': float(masked.sum()),
				'count': int(masked.count())}


			featureStatsDict[feat.GetFID()] = dict(feature_stats)

			rvds = None
			mem_ds = None
			feat = vlyr.GetNextFeature()

		vds = None
		rds = None
		return featureStatsDict

	def appendMetricRasterData(self, metricRasterPath, prefix, statTypes = ['mean']):
		# appends raster statistics to accumulation zones
		# computed statistics are min, max, mean, std, sum, count
		# give the statistics zou want to append to statTypes as list

		for path in self.__accumulationAreas:
			vecZonesPath = path
			# load model grid
			vecZonesSource = ogr.Open(vecZonesPath,1)
			vecZonesLayer = vecZonesSource.GetLayer(0)
			vecZonesCrs = (vecZonesLayer.GetSpatialRef())

			# load metric Raster
			metricRasterSource = gdal.Open(metricRasterPath)
			metricRasterCrs = osr.SpatialReference()
			metricRasterCrs.ImportFromWkt(metricRasterSource.GetProjectionRef())

			targetSpatialReference = osr.SpatialReference()
			targetSpatialReference.ImportFromEPSG(self.__targetEpsgCode)

			if (metricRasterCrs.ExportToProj4() != targetSpatialReference.ExportToProj4()):			
				print('Performing coordinate transformation on metric raster...')
				metricRasterPath = self.__workspace + '/temp/warpedRaster.tif'
				gdal.Warp(metricRasterPath,metricRasterSource,dstSRS=targetSpatialReference)
				# reload metric Raster
				metricRasterSource = gdal.Open(metricRasterPath)
				metricRasterCrs = osr.SpatialReference()
				metricRasterCrs.ImportFromWkt(metricRasterSource.GetProjectionRef())
				
			#get min and max value of data inside complete model area to normalize data
			stats = self.__zonalStats(self.__shapePath, metricRasterPath, globalSrcExtent=False)
			minValue = (stats[0]['min'])
			maxValue = (stats[0]['max'])

			# calculate zonal statistics
			print('computing zonal statistics')
			zonalStats = self.__zonalStats(vecZonesPath, metricRasterPath, globalSrcExtent=False)
			#print(zonalStats)

			# add fields for statistic values
			print('adding new fields to table')
			for value in statTypes:
				currentFieldName = prefix + '-' + str(value)
				vecZonesLayer, current_field_index=self.__addFieldReal(currentFieldName, vecZonesLayer)

			# fill attribute table with statistical values
			print('filling up attribute table')
			vecZonesLayerDefn = vecZonesLayer.GetLayerDefn()
			# loop through features and assign count data
			for feature in vecZonesLayer:
				currentFid = feature.GetFID()
				#print(' ' + str(currentFid) + ' ' + str(zonalStats[currentFid]))
				# loop through new fields
				for value in statTypes:
					currentFieldName = prefix + '-' + str(value)
					currentFieldIndex = vecZonesLayerDefn.GetFieldIndex(currentFieldName)
					if value in zonalStats[currentFid]:
						feature.SetField(currentFieldIndex, \
							((zonalStats[currentFid][value])-minValue)/maxValue)
					else:
						feature.SetField(currentFieldIndex, float(0))
				vecZonesLayer.SetFeature(feature)

			#printVectorLayerInfo(vecZonesLayer)

			vecZonesSource.Destroy()
			metricRasterSource = None
		self.__cleanup()



