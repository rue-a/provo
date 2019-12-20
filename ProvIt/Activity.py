from rdflib import URIRef as rdflib_URIRef
from rdflib import Literal as rdflib_Literal
from rdflib import BNode as rdflib_BNode
from rdflib.namespace import RDF, RDFS, XSD
from rdflib.term import _castPythonToLiteral

from .Node import Node
from ProvIt import utilities


class Activity(Node):
    '''
    Adds a PROV-O Activity to the graph
    '''
    def __init__(self, graph, iri, label, description, processType, scope):
        super().__init__(graph, iri, label, description)
        
        graph.add((
            iri,
            RDF.type,
            self.PROV.Activity
        ))
        if processType:
            graph.add((
                iri,
                self.GEOKUR.processType,
                rdflib_Literal(processType)
            ))
        if scope:
            stack = utilities.getStack()[1:-3]
            stack = '/'.join(stack)
            graph.add((
                iri,
                self.GEOKUR.wasCalledInScope,
                rdflib_Literal(stack)
            ))