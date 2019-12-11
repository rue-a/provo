from rdflib.namespace import Namespace as rdflib_Namespace
from rdflib.namespace import NamespaceManager as rdflib_NamespaceManager
from rdflib import Graph as rdflib_Graph
from rdflib import URIRef as rdflib_URIRef
from rdflib import Literal as rdflib_Literal
from rdflib.namespace import RDF, RDFS

from .Entity import Entity
from .Activity import Activity


class ProvenanceEngine():
    '''
    RDF namespace-variables are written in CAPS (according to the rdflib-package) 
    '''
    def __init__(self, namespace = 'https://geokur.geo.tu-dresden.de/ex#', abbreviation = 'ex'):
        '''
        sets up a graph object which gets built up via the functions
        '''        
        namespaceManager = rdflib_NamespaceManager(rdflib_Graph())
        # add the PROV-O namespace
        self.PROV = rdflib_Namespace('http://www.w3.org/ns/prov#')
        namespaceManager.bind('prov', self.PROV, override = False)
        # set up the namespace for the project
        self.ENGINE = rdflib_Namespace(namespace)
        namespaceManager.bind(abbreviation, self.ENGINE, override = False)
        # set up the GEOKUR namespace
        self.GEOKUR = rdflib_Namespace('https://geokur.geo.tu-dresden.de/ns#')
        namespaceManager.bind('geokur', self.GEOKUR, override = False)

        self.provenanceGraph = rdflib_Graph()
        self.provenanceGraph.namespace_manager = namespaceManager

    def addDataset(self, identifier, label = None, description = None):
        '''
        adds a dataset as prov:Entity to the graph
        '''
        dataset = Entity(
            self.provenanceGraph, 
            identifier, label, 
            description, 
            namespace = self.ENGINE)
        del dataset


    def addProcess(self, identifier, label = None, description = None, type = 'default'):
        '''
        adds a process as prov:activity to the graph
        '''
        process = Activity(
            self.provenanceGraph, 
            identifier, 
            label, 
            description,
            type,
            namespace = self.ENGINE)
        del process

    def trackProvenance(self, input, process, output):
        '''
        adds tripels to the graph to describe the process according to the W3C-Rec PROV-O.
        ---> process used inputs
        ---> outputs wereGeneratedBy process
        ---> where inputs and outputs are prov:Entities and process is a prov:Activity
        '''
        # if input or output are just strings and no list of strings, covert them to a list 
        # of length 1.
        if not isinstance(input, list):
            input = [input]
        if not isinstance(output, list):
            output = [output]
        for dataset in input:
            self.provenanceGraph.add((
                rdflib_URIRef(self.ENGINE+process),
                self.PROV.used,
                rdflib_URIRef(self.ENGINE+dataset)
            ))
        for dataset in output:
            self.provenanceGraph.add((
                rdflib_URIRef(self.ENGINE+dataset),
                self.PROV.wasGeneratedBy,
                rdflib_URIRef(self.ENGINE+process)
            ))




    def printStuff(self):
        # print([n for n in self.provenanceGraph.namespace_manager.namespaces()])
        self.provenanceGraph.serialize(format='ttl', destination = './test.ttl')