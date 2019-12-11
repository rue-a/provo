from rdflib import URIRef as rdflib_URIRef
from rdflib import Literal as rdflib_Literal
from rdflib.namespace import RDF

from .Node import Node


class Activity(Node):
    def __init__(self, graph, identifier, label, description, type, namespace):

        super().__init__(graph, identifier, label, description, namespace)
        
        graph.add((
            rdflib_URIRef(namespace+identifier),
            RDF.type,
            self.PROV.Activity
        ))
        graph.add((
            rdflib_URIRef(namespace+identifier),
            self.GEOKUR.processType,
            rdflib_Literal(type)
        ))