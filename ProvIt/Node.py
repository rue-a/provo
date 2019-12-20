from rdflib.namespace import Namespace as rdflib_Namespace
from rdflib import BNode as rdflib_BNode
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
    def __init__(self, graph, iri, label, description):
        graph.add((
            iri,
            RDFS.label,
            rdflib_Literal(label)
        ))
        if description:
            graph.add((
                iri,
                RDFS.comment,
                rdflib_Literal(description)
            ))
