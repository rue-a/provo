from rdflib.namespace import Namespace as rdflib_Namespace
from rdflib.namespace import NamespaceManager as rdflib_NamespaceManager
from rdflib import Graph as rdflib_Graph
from rdflib import URIRef as rdflib_URIRef
from rdflib import Literal as rdflib_Literal
from rdflib import BNode as rdflib_BNode
from rdflib.namespace import RDF, RDFS

from .Entity import Entity
from .Activity import Activity
from .Agent import Agent


class ProvenanceEngine:
    '''
    A class with the functionality to construct an RDF graph according to the  

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
        self.NAMESPACE = rdflib_Namespace(namespace)
        namespaceManager.bind(abbreviation, self.NAMESPACE, override = False)
        # set up the GEOKUR namespace
        self.GEOKUR = rdflib_Namespace('https://geokur.geo.tu-dresden.de/ns#')
        namespaceManager.bind('geokur', self.GEOKUR, override = False)

        self.provenanceGraph = rdflib_Graph()
        self.provenanceGraph.namespace_manager = namespaceManager

        # on default the processes get attributed to no one
        self.defaultPerson = False


    def addEntity(self, label = None, description = None):
        '''
        adds a entity as prov:Entity to the graph.
        if label is None, the value of the identifier gets written in.
        '''
        
        iri = rdflib_BNode()
        iri = rdflib_URIRef(self.NAMESPACE+iri)
        entity = Entity(
            graph = self.provenanceGraph,
            iri = iri,
            label = label, 
            description = description)
        del entity
        return iri


    def addProcess(self, label = None, description = None, 
        processType = None, scope = False, agentID = None):
        '''
        adds a process as prov:activity to the graph.  
        if label is None, the value of the identifier gets written in.
        '''
        iri = rdflib_BNode()
        iri = rdflib_URIRef(self.NAMESPACE+iri)
        process = Activity(
            graph = self.provenanceGraph,
            iri = iri,
            label = label, 
            description = description,
            processType = processType,
            scope = scope)
        del process
        
        if not agentID:
            if self.defaultPerson:
                agentID = self.defaultPerson
        if agentID:
            self.associateProcessWithPerson(
                personID = agentID,
                processID = iri
            )
        return iri


    def addAgent(self, label = None, description = None, OrcID = None):
        '''
        adds a person or organization as prov:agent to the graph.
        if label is None, the value of the identifier gets written in.
        '''
        iri = rdflib_BNode()
        iri = rdflib_URIRef(self.NAMESPACE+iri)
        agent = Agent(
            graph = self.provenanceGraph,
            iri = iri,
            label = label, 
            description = description,
            OrcID = OrcID)
        del agent
        return iri

    def relateProcessAndEntities(self, inputIDs, outputIDs, processID):
        '''
        adds tripels to the graph to describe the process according to the W3C-Rec PROV-O.
        ---> process used inputs
        ---> outputs wereGeneratedBy process
        ---> where inputs and outputs are prov:Entities and process is a prov:Activity
        '''
        # if input or output are just strings and no list of strings, covert them to a list 
        # of length 1.

        if not isinstance(inputIDs, list):
            inputIDs = [inputIDs]
        if not isinstance(outputIDs, list):
            outputIDs = [outputIDs]
        for inputID in inputIDs:
            self.provenanceGraph.add((
                processID,
                self.PROV.used,
                inputID
            ))
        for outputID in outputIDs:
            self.provenanceGraph.add((
                outputID,
                self.PROV.wasGeneratedBy,
                processID
            ))
            for inputID in inputIDs:
                self.provenanceGraph.add((
                    outputID,
                    self.PROV.wasDerivedFrom,
                    inputID
                ))


    def relatePersonsAndOrganizations(self, personIDs, organizationIDs):
        '''
        build prov:actedOnBehalfOf links between the provided persons and
        organizations.
        The Identifiers of the persons and organizations are requested!
        They can be provided either as list of strings or as single string.
        '''
        if not isinstance(personIDs, list):
            personIDs = [personIDs]
        if not isinstance(organizationIDs, list):
            organizationIDs = [organizationIDs]
        for person in personIDs:
            for organization in organizationIDs:
                self.provenanceGraph.add((
                    person,
                    self.PROV.actedOnBehalfOf,
                    organization
                ))


    def associateProcessWithPerson(self, personID, processID):
        '''
        relates a specific person to a process
        The Identifiers of the persons and organizations are requested!
        '''
        self.provenanceGraph.add((
            processID,
            self.PROV.wasAssociatedWith,
            personID
        ))

    def attributeEntitiesToAgent(self, entityIDs, agentID):
        '''
        attributes entities to a person
        entities can come as list or single
        '''
        if not isinstance(entityIDs, list):
            entityIDs = [entityIDs]
        for entityID in entityIDs:
            self.provenanceGraph.add((
                entityID,
                self.PROV.wasAttributedTo,
                agentID
            ))

    def setupDefaultPerson(self, label, description, OrcID):
        '''
        Sets up a person as prov:agent to whom all processes are automatically
        get attributed to. In the most common case this should be the person developing
        the processes and using this package to track the provenance.
        '''
        self.defaultPerson = self.addAgent(
            label = label,
            description = description,
            OrcID = OrcID
        )
        return self.defaultPerson
        


    def serialize(self, name):
        # print([n for n in self.provenanceGraph.namespace_manager.namespaces()])
        self.provenanceGraph.serialize(format='ttl', destination = name)