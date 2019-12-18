from rdflib import URIRef as rdflib_URIRef
from rdflib.namespace import RDF

from .Node import Node


class Entity(Node):
    '''
    Adds a PROV-O Entity to the graph
    '''
    def __init__(self, graph, identifier, label, description, namespace):
        super().__init__(graph, identifier, label, description, namespace)
        
        graph.add((
            rdflib_URIRef(namespace+identifier),
            RDF.type,
            self.PROV.Entity
        ))