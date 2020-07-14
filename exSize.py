# %%
from rdflib import Graph, Literal, BNode, URIRef, Namespace
from rdflib.namespace import DC, FOAF, RDF, RDFS
PROV = Namespace("http://www.w3.org/ns/prov#")
GEOKUR =  Namespace("https://geokur.geo.tu-dresden.de/namespace#")

arcGisBuffer = "https://pro.arcgis.com/en/pro-app/tool-reference/feature-analysis/create-buffers.htm"


import ProvGraph
import drawGraph

g = ProvGraph.ProvGraph(namespace='https://exGernal.org/')


intersectOut = g.addData('intersect Output')
dissolve = g.addProcess('Low Importance')
dissOut = g.addData('dissolve Output')
g.link(
    inputs=intersectOut,
    process=dissolve,
    outputs=dissOut
)
g.tagProcess(dissolve, ['import'])

multi = g.addProcess('High importance')
singleOut = g.addData('singlepart Output')
g.link(
    inputs=dissOut,
    process=multi,
    outputs=singleOut
)
g.tagProcess(multi,['wildcard', 'irreversible'])

sel2 = g.addProcess('Mid Importance')
final = g.addData('Output Potential Habitat')
g.link(
    inputs=singleOut,
    process=sel2,
    outputs=final
)
g.tagProcess(sel2, ['selection'])

sel3 = g.addProcess('ok Importance')
finals = g.addData('out')
g.link(
    inputs=final,
    process=sel3,
    outputs=finals
)
g.tagProcess(sel3, ['selection', 'parameterizable'])

g.infereWasInformedByLinks()
g.addIOTags()
g.calcRelativeImportance()

path = './out/exGernal.rdf'
g.serialize(format = 'n3', destination = path)
drawGraph.draw(graph = g, path = './graphics/exGernal.png') 

count = 0
while len([k for k in g.triples((None, RDF.type, GEOKUR.Process))]) > 1 :
    count += 1
    outPath = g.generalize(format = 'n3', destination = './out/exGernal-' + str(count) + '.rdf')
    drawGraph.draw(graph = g, path = './graphics/exGernal-' + str(count) + '.png') 