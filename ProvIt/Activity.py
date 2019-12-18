from rdflib import URIRef as rdflib_URIRef
from rdflib import Literal as rdflib_Literal
from rdflib import BNode as rdflib_BNode
from rdflib.namespace import RDF, RDFS, XSD
from rdflib.term import _castPythonToLiteral

from .Node import Node


class Activity(Node):
    '''
    Adds a PROV-O Activity to the graph
    '''
    def __init__(self, graph, identifier, methodParameters, label, description, processType, namespace):
        super().__init__(graph, identifier, label, description, namespace)
        
        graph.add((
            rdflib_URIRef(namespace+identifier),
            RDF.type,
            self.PROV.Activity
        ))
        graph.add((
            rdflib_URIRef(namespace+identifier),
            self.GEOKUR.processType,
            rdflib_Literal(processType)
        ))
        if len(methodParameters)>0:
            bNode = rdflib_BNode()
            graph.add((
                rdflib_URIRef(namespace+identifier),
                self.GEOKUR.hasParameters,
                bNode
            ))
            for tupel in methodParameters:
                paramBNode = rdflib_BNode()
                graph.add((
                    bNode,
                    self.GEOKUR.hasParameter,
                    paramBNode
                ))
                graph.add((
                    paramBNode,
                    RDFS.label,
                    rdflib_Literal(tupel[0])
                ))
                graph.add((
                    paramBNode,
                    RDF.value,                    
                    rdflib_Literal(tupel[1])
                ))