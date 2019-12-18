from rdflib.namespace import Namespace as rdflib_Namespace
from rdflib import URIRef as rdflib_URIRef
from rdflib import Literal as rdflib_Literal
from rdflib.namespace import RDFS

class Node:   
    '''
    Class to add new Nodes to a certain graph. Has specific subclasses
    like Entity or Activity.
    ''' 
    # define additional namespaces
    PROV = rdflib_Namespace('http://www.w3.org/ns/prov#')
    GEOKUR = rdflib_Namespace('https://geokur.geo.tu-dresden.de/ns#')
    def __init__(self, graph, identifier, label, description, namespace):
        if not label:
            label = identifier
        graph.add((
            rdflib_URIRef(namespace+identifier),
            RDFS.label,
            rdflib_Literal(label)
        ))
        if description:
            graph.add((
                rdflib_URIRef(namespace+identifier),
                RDFS.comment,
                rdflib_Literal(description)
            ))

