# %%
from rdflib import Graph, Literal, BNode, URIRef, Namespace
from rdflib.namespace import DC, FOAF, RDF, RDFS
PROV = Namespace("http://www.w3.org/ns/prov#")
GEOKUR =  Namespace("https://geokur.geo.tu-dresden.de/")

arcGisBuffer = "https://pro.arcgis.com/en/pro-app/tool-reference/feature-analysis/create-buffers.htm"

import ProvGraph
import drawGraph

g = ProvGraph.ProvGraph(namespace='https://gnatcatcher.org/')

majorRoads = g.addData('Major Roads')
buffer = g.addProcess('Buffer', instanceOf = arcGisBuffer)
roadsBuffer = g.addData('Roads Buffer')
g.link(
    inputs=majorRoads, 
    process=buffer, 
    outputs=roadsBuffer
)
g.tagProcess(buffer, ['allFeatures', 'parameterizable', 'geometry', 'geoRepresentation'])


inputVeg = g.addData('Input Vegetation')
select = g.addProcess('Select')
suitableVeg = g.addData('Suitable Vegetation')
g.link(
    inputs=inputVeg, 
    process=select, 
    outputs=suitableVeg
)
g.tagProcess(select, ['cqSelection', 'irreversible'])

erase = g.addProcess('Erase')
suitMinusRoads = g.addData('Suitable Vegetation Minus Roads')
g.link(
    inputs=[suitableVeg, roadsBuffer],
    process=erase,
    outputs=suitMinusRoads
)
g.tagProcess(erase, ['irreversible', 'geometry', 'allFeatures'])

elev = g.addData('Elevations Less Than 250m')
slopes = g.addData('Slopes Less Than 40 Percent')
climate = g.addData('Climate Zones')
intersect = g.addProcess('Intersect')
intersectOut = g.addData('intersect Output')
g.tagProcess(intersect, ['irreversible', 'allFeatures', 'wildcard', 'geometry'])
g.link(
    inputs=[elev, slopes, climate, suitMinusRoads],
    process=intersect,
    outputs=intersectOut
)

dissolve = g.addProcess('dissolve')
dissOut = g.addData('dissolve Output')
g.link(
    inputs=intersectOut,
    process=dissolve,
    outputs=dissOut
)
g.tagProcess(dissolve, ['addition', 'deletion', 'allFeatures', 'irreversible'])

multi = g.addProcess('multipart To Singlepart')
singleOut = g.addData('singlepart Output')
g.link(
    inputs=dissOut,
    process=multi,
    outputs=singleOut
)
g.tagProcess(multi,['addition', 'allFeatures', 'irreversible'])

sel2 = g.addProcess('Select')
final = g.addData('Output Potential Habitat')
g.link(
    inputs=singleOut,
    process=sel2,
    outputs=final
)
g.tagProcess(sel2, ['selection', 'irreversible'])

g.infereWasInformedByLinks()
g.addIOTags()
g.calcRelativeImportance()

path = './out/gnatcatcher.rdf'
g.serialize(format = 'n3', destination = path)
drawGraph.draw(graph = g, path = './graphics/gnatcatcher.png') 

# count = 0
# while len([k for k in g.triples((None, RDF.type, GEOKUR.Process))]) > 1 :
#     count += 1
#     outPath = g.generalize(format = 'n3', destination = './out/gnatcatcher-' + str(count) + '.rdf')
#     drawGraph.draw(graph = g, path = './graphics/gnatcatcher-' + str(count) + '.png') 