from rdflib import URIRef as rdflib_URIRef
from rdflib import Literal as rdflib_Literal
from rdflib.namespace import RDF

from .Node import Node

class Agent(Node):
    '''
    Adds a PROV-O Agent to the graph

    If the Agent refers to a specific Person rather than to an organization,
    the OrcID of the Person should be provided

    If the Agents represents an organization, the website or something similar
    should be provided in description.
    '''
    def __init__(self, graph, identifier, label, description, namespace, OrcID = None):
        super().__init__(graph, identifier, label, description, namespace)
        
        graph.add((
            rdflib_URIRef(namespace+identifier),
            RDF.type,
            self.PROV.Agent
        ))
        if OrcID:
            graph.add((
                rdflib_URIRef(namespace+identifier),
                self.GEOKUR.hasOrcID,
                rdflib_Literal(OrcID)
            ))