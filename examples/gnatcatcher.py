# %%
from rdflib import Graph, Literal, BNode, URIRef, Namespace
from rdflib.namespace import DC, FOAF, RDF, RDFS
PROV = Namespace("http://www.w3.org/ns/prov#")
GEOKUR =  Namespace("https://geokur.geo.tu-dresden.de/namespace#")


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

inputVeg = g.addData('Input Vegetation')
select = g.addProcess('Select')
suitableVeg = g.addData('Suitable Vegetation')
g.link(
    inputs=inputVeg, 
    process=select, 
    outputs=suitableVeg
)
erase = g.addProcess('Erase')
suitMinusRoads = g.addData('Suitable Vegetation Minus Roads')
g.link(
    inputs=[suitableVeg, roadsBuffer],
    process=erase,
    outputs=suitMinusRoads
)
elev = g.addData('Elevations Less Than 250m')
slopes = g.addData('Slopes Less Than 40 Percent')
climate = g.addData('Climate Zones')
intersect = g.addProcess('Intersect')
intersectOut = g.addData('intersect Output')
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

multi = g.addProcess('multipart To Singlepart')
singleOut = g.addData('singlepart Output')
g.link(
    inputs=dissOut,
    process=multi,
    outputs=singleOut
)

sel2 = g.addProcess('Select')
final = g.addData('Output Potential Habitat')
g.link(
    inputs=singleOut,
    process=sel2,
    outputs=final
)

g.infereWasInformedByLinks()

path = './out/gnatcatcher.rdf'
g.serialize(format = 'n3', destination = path)
# drawGraph.draw(graph = g, path = './graphics/gnatcatcher.png') 

