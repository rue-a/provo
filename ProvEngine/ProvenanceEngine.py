from rdflib.namespace import Namespace as rdflib_Namespace
from rdflib.namespace import NamespaceManager as rdflib_NamespaceManager
from rdflib import Graph as rdflib_Graph
from rdflib import URIRef as rdflib_URIRef
from rdflib import Literal as rdflib_Literal
from rdflib.namespace import RDF, RDFS

from .Entity import Entity
from .Activity import Activity

from ProvEngine import utilities




class ProvenanceEngine:
    '''
    RDF namespace-variables are written in CAPS (according to the rdflib-package) 
    '''

    def __init__(self, namespace = 'https://your.project.com/example#', abbreviation = 'ex'):
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

    def addEntity(self, localIdentifier, label = None, description = None):
        '''
        adds a entity as prov:Entity to the graph.
        if label is None, the value of the identifier gets written in.
        '''
        methodStack = utilities.getStack()
        
        if len(methodStack) > 0:
            globalIdentifier = '---'.join(methodStack)
            globalIdentifier = '-'.join((globalIdentifier, localIdentifier))
        else:
            globalIdentifier = localIdentifier
        entity = Entity(
            self.provenanceGraph, 
            globalIdentifier, 
            label, 
            description, 
            namespace = self.ENGINE)
        del entity
        return globalIdentifier


    def addProcess(self, inputIDs, outputIDs, label = None, description = None, processType = None):
        '''
        adds a process as prov:activity to the graph.  
        if label is None, the value of the identifier gets written in.
        '''
        methodStack = utilities.getStack()
        globalIdentifier = '---'.join(methodStack)
        callerMethodParameters = utilities.getFunctionParametersAndValues()
        process = Activity(
            self.provenanceGraph, 
            globalIdentifier,
            callerMethodParameters,
            label, 
            description,
            processType,
            namespace = self.ENGINE)
        del process

        self.trackProvenance(
            input = inputIDs,
            process = globalIdentifier,
            output = outputIDs
        )
        return globalIdentifier

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
        for entity in input:
            self.provenanceGraph.add((
                rdflib_URIRef(self.ENGINE+process),
                self.PROV.used,
                rdflib_URIRef(self.ENGINE+entity)
            ))
        for outputDataset in output:
            self.provenanceGraph.add((
                rdflib_URIRef(self.ENGINE+outputDataset),
                self.PROV.wasGeneratedBy,
                rdflib_URIRef(self.ENGINE+process)
            ))
            for inputDataset in input:
                self.provenanceGraph.add((
                    rdflib_URIRef(self.ENGINE+outputDataset),
                    self.PROV.wasDerivedFrom,
                    rdflib_URIRef(self.ENGINE+inputDataset)
                ))




    def printStuff(self):
        # print([n for n in self.provenanceGraph.namespace_manager.namespaces()])
        self.provenanceGraph.serialize(format='ttl', destination = './test.ttl')