# %%
from rdflib import Graph, Literal, BNode, URIRef, Namespace
from rdflib.namespace import DC, FOAF, RDF, RDFS

import ProvGraph

# setup custom namespaces
PROV = Namespace("http://www.w3.org/ns/prov#")
GEOKUR =  Namespace("https://geokur.geo.tu-dresden.de/")
EX = Namespace("https://example.com/")

g = ProvGraph.ProvGraph()

g.bind("dc", DC)
g.bind("foaf", FOAF)
g.bind("rdf", RDF)
g.bind("rdfs", RDFS)
g.bind("geokur", GEOKUR)
g.bind("prov", PROV)
g.bind("ex", EX)

g.add((GEOKUR.Process, RDFS.subClassOf, PROV.Activity))
g.add((GEOKUR.Data, RDFS.subClassOf, PROV.Entity))
g.add((GEOKUR.hasProcessType, RDF.type, RDF.Property))

# --- end setup ---

g.addData(EX.majorRoads)
g.addProcess(EX.buffer, GEOKUR.ValueChange)
g.addData(EX.roadsBuffer)
g.link(
    inputs=EX.majorRoads, 
    process=EX.buffer, 
    outputs=EX.roadsBuffer
)


g.addData(EX.inputVegetation)
g.addProcess(EX.select, GEOKUR.BasalChange)
g.addData(EX.suitableVegetation)
g.link(
    inputs=EX.inputVegetation, 
    process=EX.select, 
    outputs=EX.suitableVegetation
)

g.addProcess(EX.erase, GEOKUR.BasalChange)
g.addData(EX.suitableVegetationMinusRoads)
g.link(
    inputs=[EX.suitableVegetation,EX.roadsBuffer],
    process=EX.erase,
    outputs=EX.suitableVegetationMinusRoads
)

g.addData(EX.elevationsLessThan250m)
g.addData(EX.slopesLessThan40Percent)
g.addData(EX.climateZones)
g.addAgent(EX.testPerson)
g.addProcess(EX.intersect, GEOKUR.CoreConcept)
g.add( (EX.intersect,RDFS.label, Literal("intersection Process")) )
g.add( (EX.intersect,RDFS.comment, Literal("intersect data to identify suitable locations")) )

g.addData(EX.intersectOutput)
g.link(
    inputs=[
        EX.elevationsLessThan250m, 
        EX.slopesLessThan40Percent, 
        EX.climateZones,
        EX.suitableVegetationMinusRoads],
    process=EX.intersect,
    outputs=EX.intersectOutput,
    agents=EX.testPerson
)

g.addProcess(EX.dissolve, GEOKUR.ValueChange)
g.addData(EX.dissolveOutput)
g.link(
    inputs=EX.intersectOutput,
    process=EX.dissolve,
    outputs=EX.dissolveOutput
)

g.addProcess(EX.multipartToSinglepart, GEOKUR.BasalChange)
g.addData(EX.singlepartOutput)
g.link(
    inputs=EX.dissolveOutput,
    process=EX.multipartToSinglepart,
    outputs=EX.singlepartOutput
)

g.addProcess(EX.select2, GEOKUR.BasalChange)
g.addData(EX.outputPotentialHabitat)
g.link(
    inputs=EX.singlepartOutput,
    process=EX.select2,
    outputs=EX.outputPotentialHabitat
)

# add some more stuff for testing purposes

# g.addProcess(EX.branchOut, GEOKUR.BasalChange)
# g.addData(EX.branchedOutData)
# g.link(
#     inputs=EX.dissolveOutput,
#     process=EX.branchOut,
#     outputs=EX.branchedOutData
# )

# g.addProcess(EX.finalize, GEOKUR.BasalChange)
# g.addData(EX.finalizedData)
# g.link(
#     inputs=EX.outputPotentialHabitat,
#     process=EX.finalize,
#     outputs=EX.finalizedData
# )

qRes = g.query(
    """
    SELECT ?p ?pp
    WHERE {
        ?p prov:used ?data .
        ?data prov:wasGeneratedBy ?pp .
    }
    """
)
for row in qRes:
    g.add((row[0], PROV.wasInformedBy, row[1]))


g.serialize(format = 'n3', destination = 'test.rdf')
print('finished')