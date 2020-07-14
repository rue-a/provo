# %%
from rdflib import Graph, Literal, BNode, URIRef, Namespace
from rdflib.namespace import DC, FOAF, RDF, RDFS
PROV = Namespace("http://www.w3.org/ns/prov#")
GEOKUR =  Namespace("https://geokur.geo.tu-dresden.de/namespace#")

arcGisEuclidDistance = "https://pro.arcgis.com/de/pro-app/tool-reference/spatial-analyst/euclidean-distance.htm"
arcGisReclassify = "https://pro.arcgis.com/de/pro-app/tool-reference/spatial-analyst/reclassify.htm"
arcGisPolygonRaster = "https://pro.arcgis.com/de/pro-app/tool-reference/conversion/polygon-to-raster.htm"
arcGisCellStatistics = "https://pro.arcgis.com/en/pro-app/tool-reference/spatial-analyst/cell-statistics.htm"
arcGisPointRaster = "https://pro.arcgis.com/en/pro-app/tool-reference/conversion/point-to-raster.htm"
arcGisCostDistance = "https://pro.arcgis.com/en/pro-app/help/data/imagery/cost-distance-global-function.htm"
arcGisCostPath = "https://pro.arcgis.com/de/pro-app/tool-reference/spatial-analyst/cost-path.htm"
arcGisRasterPolyline = "https://pro.arcgis.com/de/pro-app/tool-reference/conversion/raster-to-polyline.htm"

import ProvGraph
import drawGraph

g = ProvGraph.ProvGraph(namespace='https://newHighway.org/')


my_nature = g.addData('my_nature')
euclideanDist = g.addProcess('Euclidean Distance', instanceOf= arcGisEuclidDistance)
my_nat_dist = g.addData('My_nat_dist')
g.link(
    inputs=my_nature,
    process=euclideanDist,
    outputs=my_nat_dist
)
g.tagProcess(euclideanDist, ['allFeatures', 'geoRepresentation'])#letztes, da in der Beschreibung steht, dass intern aus einer Feature Class ein Raster gemacht wird

my_builtup = g.addData('My_BuiltUp')
euclideanDist2 = g.addProcess('Euclidean Distance (2)', instanceOf=arcGisEuclidDistance)
my_bu_dist = g.addData('My_bu_dist')
g.link(
    inputs=my_builtup,
    process=euclideanDist2,
    outputs=my_bu_dist
)
g.tagProcess(euclideanDist2, ['allFeatures', 'geoRepresentation'])

reclassify = g.addProcess('Reclassify', instanceOf=arcGisReclassify)
my_nat_ext = g.addData('My_nat_ext')
g.link(
    inputs=my_nat_dist,
    process=reclassify,
    outputs=my_nat_ext
)
g.tagProcess(reclassify, ['parameterizable', 'allFeatures'])


reclassify2 = g.addProcess('Reclassify (2)', instanceOf=arcGisReclassify)
my_bu_ext = g.addData('My_bu_ext')
g.link(
    inputs=my_bu_dist,
    process=reclassify2,
    outputs=my_bu_ext
)
g.tagProcess(reclassify2, ['parameterizable', 'allFeatures'])


my_LandUse_2006 = g.addData('My_LandUse_2006')
polygonRaster = g.addProcess('Polygon to Raster', instanceOf=arcGisPolygonRaster)
Route1_cost = g.addData('Route1_cost')
g.link(
    inputs=my_LandUse_2006,
    process=polygonRaster,
    outputs=Route1_cost
)
g.tagProcess(polygonRaster, ['geoRepresentation', 'geometry'])


cellStatistics = g.addProcess('Cell Statistics', instanceOf=arcGisCellStatistics)
Route2_cost = g.addData('Route2_cost')
g.link(
    inputs=[Route1_cost, my_bu_ext, my_nat_ext],
    process=cellStatistics,
    outputs=Route2_cost
)
g.tagProcess(cellStatistics, ['sensitive', 'allFeatures', 'addition'])#hier bin ich mir aber sehr unsicher bei der Einordnung


endpoint = g.addData('Endpoint')
pointRaster = g.addProcess('Point to Raster', instanceOf=arcGisPointRaster)
endraster = g.addData('endraster')
g.link(
    inputs=endpoint,
    process=pointRaster,
    outputs=endraster
)
g.tagProcess(pointRaster, ['geoRepresentation', 'allFeatures'])


costDistance = g.addProcess('Cost Distance (2)', instanceOf=arcGisCostDistance)
Route2_back = g.addData('Route2_back')
Route2_dist = g.addData('Route2_dist')
g.link(
    inputs=[Route2_cost, endraster],
    process=costDistance,
    outputs=[Route2_back, Route2_dist]
)
g.tagProcess(costDistance, ['allFeatures', 'sensitive', 'deletion'])


beginpoint = g.addData('Beginpoint')
pointRaster2 = g.addProcess('Point to Raster (2)', instanceOf=arcGisPointRaster)
beginraster = g.addData('beginraster')
g.link(
    inputs=beginpoint,
    process=pointRaster2,
    outputs=beginraster
)
g.tagProcess(pointRaster2, ['geoRepresentation', 'allFeatures'])


costPath = g.addProcess('Cost Path (2)', instanceOf=arcGisCostPath)
CostPat_endr1 = g.addData('CostPat_endr1')
g.link(
    inputs=[beginraster, Route2_dist, Route2_back],
    process=costPath,
    outputs=CostPat_endr1
)
g.tagProcess(costPath, ['allFeatures', 'sensitive'])


rasterPolyline = g.addProcess('Raster to Polyline (2)', instanceOf=arcGisRasterPolyline)
myRoute = g.addAgent('MyRoute')
g.link(
    inputs=CostPat_endr1,
    process=rasterPolyline,
    outputs=myRoute
)
g.tagProcess(rasterPolyline, 'geoRepresentation')



g.infereWasInformedByLinks()
g.addIOTags()
g.calcRelativeImportance()

path = './out/newHighway.rdf'
g.serialize(format = 'n3', destination = path)
drawGraph.draw(graph = g, path = './graphics/newHighway.png') 

count = 0
while len([k for k in g.triples((None, RDF.type, GEOKUR.Process))]) > 1 :
    count += 1
    outPath = g.generalize(format = 'n3', destination = './out/newHighway-' + str(count) + '.rdf')
    drawGraph.draw(graph = g, path = './graphics/newHighway-' + str(count) + '.png') 