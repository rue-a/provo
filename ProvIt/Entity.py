from rdflib.namespace import RDF

from .Node import Node


class Entity(Node):
    '''
    Adds a PROV-O Entity to the graph
    '''
    def __init__(self, graph, iri, label, description):
        super().__init__(graph, iri, label, description)
                
        graph.add((
            iri,
            RDF.type,
            self.PROV.Entity
        ))
