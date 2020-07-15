from __future__ import annotations
from datetime import datetime

from rdflib import Graph, Literal, BNode, URIRef, Namespace
from rdflib.namespace import DC, FOAF, RDF, RDFS, PROV, XSD

# this document implements the basic scheme of PROV-O 
# https://www.w3.org/TR/prov-o/

class Node():
    def __init__(self, graph, id):        
        self.id = URIRef(graph.getCNS() + id)
        self.graph = graph

    def label(self, label):
        self.graph.add((self.id, RDFS.label, Literal(label)))

    def description(self, description):
        self.graph.add((self.id, RDFS.comment, Literal(description)))

    def getId(self):
        return self.id


class Activity(Node):
    """
    Instantiates a PROV-O Activity object with the basic
    relations

    Methods
    ---
    wasInformedBy (self, activity: Activity)
    """
    def __init__(self, graph, id):
        super().__init__(graph = graph, id = id)
        self.graph.add((self.id, RDF.type, PROV.Activity))

    def wasInformedBy(self, activity: Activity):
        assert(isinstance(activity, Activity))
        self.graph.add((self.id, PROV.wasInformedBy, activity.getId()))

    def used(self, entity: Entity):
        assert(isinstance(entity, Entity))
        self.graph.add((self.id, PROV.used, entity.getId()))

    def wasAssociatedWith(self, agent: Agent):
        assert(isinstance(agent, Agent))
        self.graph.add((self.id, PROV.wasAssociatedWith, agent.getId()))

    def startedAtTime(self, in_datetime: datetime):
        assert(isinstance(in_datetime, datetime))
        self.graph.add((self.id, PROV.startedAtTime, Literal(in_datetime, datatype = XSD.datetime)))
    
    def endedAtTime(self, in_datetime: datetime):
        assert(isinstance(in_datetime, datetime))
        self.graph.add((self.id, PROV.endedAtTime, Literal(in_datetime, datatype = XSD.datetime)))


class Entity(Node):
    def __init__(self, graph, id):
        super().__init__(graph = graph, id = id)
        self.graph.add((self.id, RDF.type, PROV.Entity))
    
    def wasDerivedFrom(self, entity: Entity):
        assert(isinstance(entity, Entity))
        self.graph.add((self.id, PROV.wasDerivedFrom, entity.getId()))

    def wasGeneratedBy(self, activity: Activity):
        assert(isinstance(activity, Activity))
        self.graph.add((self.id, PROV.wasGeneratedBy, activity.getId()))

    def wasAttributedTo(self, agent: Agent):
        assert(isinstance(agent, Agent))
        self.graph.add((self.id, PROV.wasAttributedTo, agent.getId()))
    
class Agent(Node):
    def __init__(self, graph, id):
        super().__init__(graph = graph, id = id)
        self.graph.add((self.id, RDF.type, PROV.Agent))

    def actedOnBehalfOf(self, agent: Agent):
        assert(isinstance(agent, Agent))
        self.graph.add((self.id, PROV.actedOnBehalfOf, agent.getId()))
