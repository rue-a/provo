from rdflib.namespace import Namespace as rdflib_Namespace
from rdflib.namespace import NamespaceManager as rdflib_NamespaceManager
from rdflib import Graph as rdflib_Graph
from rdflib import URIRef as rdflib_URIRef
from rdflib import Literal as rdflib_Literal
from rdflib.namespace import RDF, RDFS

from .Entity import Entity
from .Activity import Activity
from .Agent import Agent

from ProvIt import utilities




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
        self.ENGINE = rdflib_Namespace(namespace)
        namespaceManager.bind(abbreviation, self.ENGINE, override = False)
        # set up the GEOKUR namespace
        self.GEOKUR = rdflib_Namespace('https://geokur.geo.tu-dresden.de/ns#')
        namespaceManager.bind('geokur', self.GEOKUR, override = False)

        self.provenanceGraph = rdflib_Graph()
        self.provenanceGraph.namespace_manager = namespaceManager

        # on default the processes get attributed to no one
        self.attributedPerson = False


    def addEntity(self, localIdentifier, label = None, description = None):
        '''
        adds a entity as prov:Entity to the graph.
        if label is None, the value of the identifier gets written in.
        To prevent duplicates the global identifier(IRI) of the Node gets constructed 
        from the current scope and the local Identifier.
        '''
        
        # on the first position of the stack is the '<module>', 
        # we do not need this. We neither need the last two entries
        # of the list. The last one refers to the getStack()-method 
        # itself, the 2nd last one to the method from where getStack()
        # is called

        methodStack = utilities.getStack()[1:-2]        
        
        if len(methodStack) > 0:
            globalIdentifier = '---'.join(methodStack)
            globalIdentifier = '-'.join((globalIdentifier, localIdentifier))
        else:
            globalIdentifier = localIdentifier

        entityID = self.addFlatEntity(
            globalIdentifier = globalIdentifier,
            label = label,
            description = description
        )
        return entityID


    def addProcess(self, inputIDs, outputIDs, label = None, description = None, processType = None,
        agentID = None):
        '''
        adds a process as prov:activity to the graph.  
        if label is None, the value of the identifier gets written in.

        The input and output IDs are the identifiers of the regarding Entities.
        they can be provided as list of strings or as a single string.

        If agentID is not None, the process gets attributed to this prov:agent. Then, 
        if the class variable attributedPerson is not None, the process get attributed
        to this prov:agent. If both are None, the process doesn't get attributed to 
        anyone.

        The Identifier(IRI) of the Process is automatically generated as combination
        of the current scope in the program and the name of the method from where 
        addProcess(...) is called. This way the possibility of duplicated URIs is
        erased. This way we also save the information how deep in the program the
        process was called.

        '''

        # on the first position of the stack is the '<module>', 
        # we do not need this. We neither need the last two entries
        # of the list. The last one refers to the getStack()-method 
        # itself, the 2nd last one to the method from where getStack()
        # is called.
        methodStack = utilities.getStack()[1:-2]
        globalIdentifier = '---'.join(methodStack)
        # get the params and vals from the method from where this addProcess(...)
        # was called. They come as Tupels.
        callerMethodParameters = utilities.getMethodParametersAndValues(2)
        process = Activity(
            self.provenanceGraph, 
            globalIdentifier,
            callerMethodParameters,
            label, 
            description,
            processType,
            namespace = self.ENGINE)
        del process

        self.relateProcessAndEntities(
            inputIDs = inputIDs,            
            outputIDs = outputIDs,
            processID = globalIdentifier,
        )

        if agentID:
            self.attributeProcessToPerson(
                personID = self.ENGINE + agentID,
                processID = self.ENGINE + globalIdentifier
            )
        elif self.attributedPerson:
            self.attributeProcessToPerson(
                personID = self.ENGINE + self.attributedPerson,
                processID = self.ENGINE + globalIdentifier
            )

        return globalIdentifier


    def addFlatAgent(self, globalIdentifier, label = None, description = None, OrcID = None):
        '''
        adds a entity as prov:Entity to the graph.
        if label is None, the value of the identifier gets written in.
        '''
        agent = Agent(
            self.provenanceGraph, 
            globalIdentifier, 
            label, 
            description, 
            namespace = self.ENGINE,
            OrcID = OrcID)
        del agent
        return globalIdentifier


    def addFlatEntity(self, globalIdentifier, label = None, description = None):
        '''
        adds a entity as prov:Entity to the graph.
        if label is None, the value of the identifier gets written in.
        '''
        entity = Entity(
            self.provenanceGraph, 
            globalIdentifier, 
            label, 
            description, 
            namespace = self.ENGINE)
        del entity
        return globalIdentifier


    def addFlatProcess(self, globalIdentifier, label = None, description = None, 
        processType = None, paramsAndVals = None):
        '''
        adds a process as prov:activity to the graph.  
        if label is None, the value of the identifier gets written in.
        '''
        process = Activity(
            self.provenanceGraph, 
            globalIdentifier,
            label, 
            description,
            processType,            
            paramsAndVals,
            namespace = self.ENGINE)
        del process

        return globalIdentifier


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
        for entity in inputIDs:
            self.provenanceGraph.add((
                rdflib_URIRef(self.ENGINE+processID),
                self.PROV.used,
                rdflib_URIRef(self.ENGINE+entity)
            ))
        for outputDataset in outputIDs:
            self.provenanceGraph.add((
                rdflib_URIRef(self.ENGINE+outputDataset),
                self.PROV.wasGeneratedBy,
                rdflib_URIRef(self.ENGINE+processID)
            ))
            for inputDataset in inputIDs:
                self.provenanceGraph.add((
                    rdflib_URIRef(self.ENGINE+outputDataset),
                    self.PROV.wasDerivedFrom,
                    rdflib_URIRef(self.ENGINE+inputDataset)
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
                    rdflib_URIRef(person),
                    self.PROV.actedOnBehalfOf,
                    rdflib_URIRef(organization)
                ))


    def attributeProcessToPerson(self, personID, processID):
        '''
        relates a specific person to a process
        The Identifiers of the persons and organizations are requested!
        '''
        self.provenanceGraph.add((
            rdflib_URIRef(processID),
            self.PROV.wasAttributedTo,
            rdflib_URIRef(personID)
        ))

    def setupAttributedPerson(self, identifier, label, description, OrcID):
        '''
        Sets up a person as prov:agent to whom all non-flat process are automatically
        get attributed to. In the most common case this should be the person developing
        the processes and using this package to track the provenance.
        '''
        self.attributedPerson = self.addFlatAgent(
            globalIdentifier = identifier,
            label = label,
            description = description,
            OrcID = OrcID)
        


    def serialize(self, name):
        # print([n for n in self.provenanceGraph.namespace_manager.namespaces()])
        self.provenanceGraph.serialize(format='ttl', destination = name)