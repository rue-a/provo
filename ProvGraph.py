from rdflib import Graph, Literal, BNode, URIRef, Namespace
from rdflib.namespace import DC, FOAF, RDF, RDFS
from rdflib.plugins.sparql import prepareQuery
import pandas as pd
import csv

import drawGraph
# setup namespaces
PROV = Namespace("http://www.w3.org/ns/prov#")
GEOKUR =  Namespace("https://geokur.geo.tu-dresden.de/namespace#")

class ProvGraph(Graph):
    CNS = Namespace("https://customNamespace.com/")
    def __init__(self, store='default', namespace = None, identifier=None, namespace_manager=None):
        super().__init__(store=store, identifier=identifier, namespace_manager=namespace_manager)
        if namespace:
            self.CNS = Namespace(namespace)
        self.add((GEOKUR.Process, RDFS.subClassOf, PROV.Activity))
        self.add((GEOKUR.SubProcess, RDFS.subClassOf, PROV.Activity))
        self.add((GEOKUR.Data, RDFS.subClassOf, PROV.Entity))
        self.add((GEOKUR.isInstanceOf, RDF.type, RDF.Property))        
        self.add((GEOKUR.isInstanceOf, RDFS.domain, GEOKUR.Process))
        self.bind("dc", DC)
        self.bind("foaf", FOAF)
        self.bind("rdf", RDF)
        self.bind("rdfs", RDFS)
        self.bind("geokur", GEOKUR)
        self.bind("prov", PROV)
        self.bind("cns", self.CNS)
    # methods for construction of the prov graph
    def addProcess(self, label, instanceOf = None):
        ID = eval('self.CNS.' + BNode())
        self.add((ID, RDF.type, GEOKUR.Process))
        self.add((ID, RDFS.label, Literal(label)))
        if (instanceOf):
            self.add((ID, GEOKUR.isInstanceOf, URIRef(instanceOf)))
        return ID
    def addData(self, label):
        ID = eval('self.CNS.' + BNode())
        self.add((ID, RDF.type, GEOKUR.Data))
        self.add((ID, RDFS.label, Literal(label)))
        return ID
    def addAgent(self, label):
        ID = eval('self.CNS.' + BNode())
        self.add((ID, RDF.type, GEOKUR.Agent))
        self.add((ID, RDFS.label, Literal(label)))
        return ID
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
                self.add((process, PROV.used, entity))
        if (outputs and process):
            for entity in outputs:
                self.add((entity, PROV.wasGeneratedBy, process))
        if (inputs and outputs):
            for inp in inputs:
                for out in outputs:
                    self.add((out, PROV.wasDerivedFrom, inp))
        if (agents and inputs): 
            for agent in agents:
                for inp in inputs:
                    self.add((inp, PROV.wasAttributedTo, agent))
        if (agents and outputs):
            for agent in agents:
                for output in outputs:
                    self.add((output, PROV.wasAttributedTo, agent))
        if (agents and process):
            for agent in agents:
                self.add((process, PROV.wasAssociatedWith, agent))
    
    def infereWasInformedByLinks(self):
        qRes = self.query(
            """SELECT ?p ?pp
            WHERE {
                ?p prov:used ?data .
                ?data prov:wasGeneratedBy ?pp .
            }"""
        )
        for row in qRes:
            self.add((row[0], PROV.wasInformedBy, row[1]))