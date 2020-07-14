# %%
from rdflib import Graph, Literal, BNode, URIRef, Namespace
from rdflib.namespace import DC, FOAF, RDF, RDFS
PROV = Namespace("http://www.w3.org/ns/prov#")
GEOKUR =  Namespace("https://geokur.geo.tu-dresden.de/namespace#")

arcGisBuffer = "https://pro.arcgis.com/en/pro-app/tool-reference/feature-analysis/create-buffers.htm"
arcGisIntersect = "https://pro.arcgis.com/de/pro-app/tool-reference/analysis/intersect.htm"
arcGisErase = "https://pro.arcgis.com/de/pro-app/tool-reference/analysis/erase.htm"
arcGisFeatureRaster = "https://pro.arcgis.com/de/pro-app/tool-reference/raster-analysis/convert-feature-to-raster.htm"
arcGisExtractMask = "https://pro.arcgis.com/de/pro-app/tool-reference/spatial-analyst/extract-by-mask.htm"
arcGisZonalTable = "https://pro.arcgis.com/de/pro-app/tool-reference/spatial-analyst/zonal-statistics-as-table.htm"
arcGisJoinField = "https://pro.arcgis.com/de/pro-app/tool-reference/data-management/join-field.htm"
arcGisCalculateField = "https://pro.arcgis.com/de/pro-app/tool-reference/data-management/calculate-field.htm"

import ProvGraph
import drawGraph

g = ProvGraph.ProvGraph(namespace='https://chinaNighlights.org/')

train_stations = g.addData('train_stations')
buffer = g.addProcess('Buffer', instanceOf=arcGisBuffer)
stationBuffer = g.addData('Ch_Stations_Buffer')
g.link(
    inputs=train_stations,
    process=buffer,
    outputs=stationBuffer
)
g.tagProcess(buffer, ['parameterizable', 'geometry', 'geoRepresentation', 'allFeatures'])


China_border = g.addData('China_border')
gas_flares = g.addData('gas_flares')
erase = g.addProcess('Erase', instanceOf=arcGisErase)
CHN_adm0_Erase = g.addData('CHN_adm0_Erase')
g.link(
    inputs=[China_border, gas_flares],
    process=erase,
    outputs=CHN_adm0_Erase
)
g.tagProcess(erase, ['irreversible', 'geometry', 'allFeatures'])


intersect = g.addProcess('Intersect', instanceOf = arcGisIntersect)
CHN_adm0_Erase_Intersect = g.addData('CHN_adm0_Erase_Intersect')
g.link(
    inputs=[CHN_adm0_Erase, stationBuffer],
    process=intersect,
    outputs=CHN_adm0_Erase_Intersect
)
g.tagProcess(intersect, ['irreversible', 'allFeatures', 'geometry'])


featureRaster = g.addProcess('Feature to Raster', instanceOf=arcGisFeatureRaster)
Feature_CHN_1 = g.addData('Feature_CHN_1')
g.link(
    inputs=CHN_adm0_Erase_Intersect,
    process=featureRaster,
    outputs=Feature_CHN_1
)
g.tagProcess(featureRaster, ['geoRepresentation', 'geometry', 'allFeatures', 'irreversible'])


night_lights_1 = g.addData('F101993-night_lights.tif')
extractMask = g.addProcess('Extract by Mask', instanceOf= arcGisExtractMask)
Extract_tif1 = g.addData('Extract_tif1')
g.link(
    inputs=[night_lights_1, Feature_CHN_1],
    process=extractMask,
    outputs=Extract_tif1
)
g.tagProcess(extractMask, ['allFeatures', 'deletion', 'geoRepresentation']) 


night_lights_2 = g.addData('F182013-night_lights.tif')
extractMask2 = g.addProcess('Extract by Mask 2', instanceOf=arcGisExtractMask)
Extract_tif1_2 = g.addData('Extract_tif1(2)')
g.link(
    inputs=[night_lights_2, Feature_CHN_1],
    process=extractMask2,
    outputs=Extract_tif1_2
)
g.tagProcess(extractMask2, ['allFeatures', 'deletion', 'geoRepresentation'])


admin_units = g.addData('admin_units')
zonalTab = g.addProcess('Zonal Statistics as Table', instanceOf=arcGisZonalTable)
ZonalSt_shp2 = g.addData('ZonalSt_shp2')
g.link(
    inputs=[Extract_tif1, admin_units],
    process=zonalTab,
    outputs=ZonalSt_shp2
)
g.tagProcess(zonalTab, ['sensitive', 'addition', 'allFeatures'])#hier bin ich mir sehr unsicher, da sich die Statistik schon verändert, wenn sich die Eingabewerten verändern


zonalTab2 = g.addProcess('Zonal Statistics as Table (2)', instanceOf= arcGisZonalTable)
ZonalSt_shp1 = g.addData('ZonalSt_shp1')
g.link(
    inputs=[Extract_tif1_2, admin_units],
    process=zonalTab2,
    outputs=ZonalSt_shp1
)
g.tagProcess(zonalTab2, ['sensitive', 'addition', 'allFeatures']) #s.o.


joinField = g.addProcess('Join Field', instanceOf=arcGisJoinField)
ZonalSt_shp1_2 = g.addData('ZonalSt_shp1(2)')
g.link(
    inputs=[ZonalSt_shp1, ZonalSt_shp2],
    process=joinField,
    outputs=ZonalSt_shp1_2
)
g.tagProcess(joinField, ['addition', 'deletion'])

calculateField = g.addProcess('Calculate Field', instanceOf=arcGisCalculateField)
Luminosity_change = g.addData('Luminosity_change')
g.link(
    inputs=ZonalSt_shp1_2,
    process=calculateField,
    outputs=Luminosity_change
)
g.tagProcess(calculateField, 'allFeatures')


g.infereWasInformedByLinks()
g.addIOTags()
g.calcRelativeImportance()

path = './out/chinaNighlights.rdf'
g.serialize(format = 'n3', destination = path)
drawGraph.draw(graph = g, path = './graphics/chinaNighlights.png') 

count = 0
while len([k for k in g.triples((None, RDF.type, GEOKUR.Process))]) > 1 :
    count += 1
    outPath = g.generalize(format = 'n3', destination = './out/chinaNighlights-' + str(count) + '.rdf')
    drawGraph.draw(graph = g, path = './graphics/chinaNighlights-' + str(count) + '.png') 