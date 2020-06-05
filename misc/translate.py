# %%
from rdflib import Graph, Literal, BNode, URIRef, Namespace
from rdflib.namespace import DC, FOAF, RDF, RDFS

import ProvGraph
from translateMethods import *

# gather annotations
path = './20200514_variabilityModelled.R'

annotations = gatherAnnotations(path)
init = path
authors = []
organizations = []
labels = []
descriptions = []
units = []
linkedFiles = []
for annotation in annotations:
    split = annotation.split(' ',1)
    keyword = split[0].split('.',1)
    if keyword[1] == 'init':
        if len(split)>1:
            init = split[1]
    if keyword[1] == 'author':
        authors.append(split[1])
    if keyword[1] == 'organization':
        organizations.append(split[1])
    if keyword[1] == 'label':
        labels.append(split[1])
    if keyword[1] == 'description':
        descriptions.append(split[1])
    if keyword[1] == 'unit':
        print(split[1])
        units.append(split[1].replace('.', '').replace('[', '').replace(']', ''))
    if keyword[1] == 'linkFile':
        linkedFiles.append(split[1])
    

# setup
PROV = Namespace("http://www.w3.org/ns/prov#")
GEOKUR = Namespace("https://geokur.geo.tu-dresden.de/")

g = ProvGraph.ProvGraph()

g.bind("dc", DC)
g.bind("foaf", FOAF)
g.bind("rdf", RDF)
g.bind("rdfs", RDFS)
g.bind("geokur", GEOKUR)
g.bind("prov", PROV)


g.add((GEOKUR.Process, RDFS.subClassOf, PROV.Activity))
g.add((GEOKUR.Data, RDFS.subClassOf, PROV.Entity))
g.add((GEOKUR.hasProcessType, RDF.type, RDF.Property))
# --- end setup ---

# begin parsing

cns = parseInit(init)
CNS = eval(cns)
# bind custom namespace
g.bind("cns", CNS)

for unit in units:
    parseUnit(unit)
    # print(unit)
    data, process, link = parseUnit(unit)
    # print(data)
    # print(process)
    for dat in data:
        eval("g." + dat)
    procID = eval("g." + process).split('/')[-1]
    eval("g." + link[0] + procID + link[1])

for author in authors:
    g.addAgent(eval("CNS." + author))

for organization in organizations:
    g.addAgent(eval("CNS." + organization))

for label in labels:
    g.add((eval("CNS." + label.split(' ', 1)[0]), RDFS.label, Literal(label.split(' ', 1)[1])))

for description in descriptions:
    g.add((eval("CNS." + description.split(' ', 1)[0]), RDFS.comment, Literal(description.split(' ', 1)[1])))



for author in authors:
    for organization in organizations:
        g.add((eval("CNS." + author), PROV.actedOnBehalfOf , eval("CNS." + organization)))

qRes = g.query(
    """
    SELECT ?data
    WHERE {
        ?data a geokur:Data .
    }
    """
)
for row in qRes:
    g.add((row[0], RDF.type, PROV.Entity))
    for author in authors:
        g.add((row[0], PROV.wasAttributedTo, eval("CNS." + author)))
    for organization in organizations:
        g.add((row[0], PROV.wasAttributedTo, eval("CNS." + organization)))

qRes = g.query(
    """
    SELECT ?process
    WHERE {
        ?process a geokur:Process .
    }
    """
)
for row in qRes:
    g.add((row[0], RDF.type, PROV.Activity))
    for author in authors:
        g.add((row[0], PROV.wasAssociatedWith, eval("CNS." + author)))
    for organization in organizations:
        g.add((row[0], PROV.wasAssociatedWith, eval("CNS." + organization)))

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