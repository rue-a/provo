# %%

# @prov.init
# @prov.author arne

from shapely.geometry import shape, Polygon, MultiPolygon, MultiLineString
from sentinelhub import WmsRequest, WcsRequest, MimeType, CRS, BBox, BBoxSplitter, CRS, DataSource, CustomUrlParam
import datetime
import os, shutil
import numpy as np
import matplotlib.pyplot as plt
import utm


def calcSize(bottomLeft, upperRight):
    # @prov.description calcSize calcs horizontal and vertical size of a bbox im meters
    upperRight_utm = utm.from_latlon(upperRight[1], upperRight[0])
    bottomLeft_utm = utm.from_latlon(bottomLeft[1], bottomLeft[0])
    verticalDistance = abs(upperRight_utm[1] - bottomLeft_utm[1])
    horizontalDistance = abs(upperRight_utm[0] - bottomLeft_utm[0])
    return horizontalDistance, verticalDistance

def calcBBoxSplits(horizontalDistance, verticalDistance, groundRes = 10):
    # @prov.description calcBBoxSplits calc nb of horizontal and vertical splits to stay 
    # below 5000 pixels length.
    
    horizontalLength = horizontalDistance / groundRes
    verticalLength = verticalDistance / groundRes
    # hor length leads to vertical splits
    verticalSplits = int(horizontalLength / 5000)
    horizontalSplits = int(verticalLength / 5000)
    return horizontalSplits, verticalSplits




dataDir = './data/temp'
mosaicName = 'ddMosaic.tif'
INSTANCE_ID = '...'


bottomLeft = (13.15, 50.822)
upperRight = (14.25, 51.185)
poly = Polygon([
    (bottomLeft[0], bottomLeft[1]),
    (bottomLeft[0], upperRight[1]),
    (upperRight[0], upperRight[1]),
    (upperRight[0], bottomLeft[1])
    ])

# @prov.unit horizontalDistance, verticalDistance = calcSize(bottomLeft, upperRight)
horizontalDistance, verticalDistance = calcSize(bottomLeft, upperRight)

# @prov.unit horizontalSplits, verticalSplits = calcBBoxSplits(bottomLeft, upperRight) valueChange
horizontalSplits, verticalSplits = calcBBoxSplits(horizontalDistance, verticalDistance)

print(horizontalDistance,verticalDistance)
print(horizontalSplits, verticalSplits)

# @prov.unit bbox_list = bbox_splitter(areaOfInterest, verticalSplits, horizontalSplits) semanticShift
# @prov.label areaOfInterest bbox of dresden 
# @prov.description areaOfInterest bottomLeft = (13.15, 50.822), upperRight = (14.25, 51.185), wgs84
bbox_splitter = BBoxSplitter(shape_list=[poly], crs = CRS.WGS84, split_shape = (verticalSplits+1, horizontalSplits+1))
# @prov.description bbox_splitter splits a given polygon into multiple parts
# :param split_shape: Parameter that describes the shape in which the area 
# bounding box will be split. It can be a tuple of the form (n, m) which means 
# the area bounding box will be split into n columns and m rows. It can also 
# be a single integer n which is the same as (n, n).
bbox_list = bbox_splitter.get_bbox_list()
info_list = bbox_splitter.get_info_list()
print(bbox_list)

# %%
# @prov.unit rastersets = downloadImagery (bbox_list) coreConcept
# @prov.description downloadImagery downloads imagery data from ESA Sentinel Hub for each Bbox
# in bbox_list. Then loads them in a list called rastersets
for bbox in bbox_list:    
    wcs_trueColor_request = WcsRequest(
        layer='EXPERIMENTAL',
        data_folder=dataDir,
        bbox=bbox,
        time='2020-02-08',
        image_format=MimeType.TIFF_d32f,
        resx = '10m', 
        resy = '10m',
        instance_id=INSTANCE_ID,
        maxcc=0.3,
        custom_url_params={
        #     CustomUrlParam.ATMFILTER: 'ATMCOR',
            CustomUrlParam.SHOWLOGO: False
        }
        )
    wcs_trueColor_request.save_data()
print('finished downloading')


# %%
import rasterio
rastersets = []
for filename in os.listdir(dataDir):
    path = dataDir + '/' + filename
    rasterset = rasterio.open(path)
    rastersets.append(rasterset)

# @prov.unit mosaic = merge(rastersets) valueChange
# @prov.description merge merges all rasters from a list of rasters to a mosaic and adjusts 
# metadata

from rasterio.merge import merge
mosaic, transformation = merge(rastersets, nodata=1)

for source in rastersets:
    source.close()
# from rasterio.plot import show
# show(mosaic)

# get metadata from the last raster image
meta = rasterset.meta.copy()
# adjust this metadata to fit to our mosaic (namley change size)
meta.update({
    "driver": "GTiff",
    "height": mosaic.shape[1],
    "width": mosaic.shape[2],
    "transform": transformation
})

# @prov.label mosaic ./data/mosaic/ddMosaic.tif
outpath = './data/mosaics/' + mosaicName
with rasterio.open(outpath, "w", **meta) as dest:
    dest.write(mosaic)
print('done')

# %%
shutil.rmtree(dataDir)



# %%
