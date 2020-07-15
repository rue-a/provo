from rdflib import Graph, Literal, BNode, URIRef, Namespace
from rdflib.namespace import DC, FOAF, RDF, RDFS
from rdflib.plugins.sparql import prepareQuery


# setup namespaces
PROV = Namespace("http://www.w3.org/ns/prov#")
# GEOKUR =  Namespace("https://geokur.geo.tu-dresden.de/namespace#")


class ProvGraph(Graph):
    CNS = Namespace("https://customNamespace.com/")
    def __init__(self, store='default', namespace = None, identifier=None, namespace_manager=None):
        super().__init__(store=store, identifier=identifier, namespace_manager=namespace_manager)
        if namespace:
            self.CNS = Namespace(namespace)
        # self.add((GEOKUR.Process, RDFS.subClassOf, PROV.Activity))
        # self.add((GEOKUR.SubProcess, RDFS.subClassOf, PROV.Activity))
        # self.add((GEOKUR.Data, RDFS.subClassOf, PROV.Entity))
        # self.add((GEOKUR.isInstanceOf, RDF.type, RDF.Property))        
        # self.add((GEOKUR.isInstanceOf, RDFS.domain, GEOKUR.Process))
        self.bind("dc", DC)
        self.bind("foaf", FOAF)
        self.bind("rdf", RDF)
        self.bind("rdfs", RDFS)
        # self.bind("geokur", GEOKUR)
        self.bind("prov", PROV)
        self.bind("cns", self.CNS)

    def getCNS(self):
        return self.CNS

    def link(self, inputs = None, process = None, outputs = None, agents = None):
        if inputs:
            if not isinstance(inputs, list):
                inputs = [inputs]
        if outputs:
            if not isinstance(outputs, list):
                outputs = [outputs]
        if agents:
            if not isinstance(agents,list):
                agents = [agents]  

        if (inputs and process):
            for entity in inputs:
                process.used(entity)
        if (outputs and process):
            for entity in outputs:
                entity.wasGeneratedBy(process)
        if (inputs and outputs):
            for inp in inputs:
                for out in outputs:
                    out.wasDerivedFrom(inp)
        if (agents and inputs): 
            for agent in agents:
                for inp in inputs:
                    inp.wasAttributedTo(agent)
        if (agents and outputs):
            for agent in agents:
                for output in outputs:
                    output.wasAttributedTo(agent)
        if (agents and process):
            for agent in agents:
                process.wasAssociatedWith(agent)
        qRes = self.query(
            """SELECT ?p ?pp
            WHERE {
                ?p prov:used ?data .
                ?data prov:wasGeneratedBy ?pp .
            }"""
        )
        for row in qRes:
            self.add((row[0], PROV.wasInformedBy, row[1]))
        