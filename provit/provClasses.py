"""
@author Arne Rümmler
@organization TU Dresden
@contact arne.ruemmler@tu-dresden.de


@summery Implementation of the the basic scheme of PROV-O https://www.w3.org/TR/prov-o/ .
    Works in tandem with provGraph.py
@status Prototype
"""

from datetime import datetime

from rdflib import Graph, Literal, BNode, URIRef, Namespace
from rdflib.namespace import DC, FOAF, RDF, RDFS, PROV, XSD

class Node():
    """ Parent class of Activity, Agent, and Entity.
        
    Parameters
    ----------
    graph: ProvGraph
        The graph to which the node should be added.
    id: str
        The ID of the node. The ID has to be unique inside the custom 
        namespace of the ProvGraph instance. The ID also has to be 
        alphanumerical, without empty spaces.

    """
    def __init__(self, graph, id):
        """constructor: takes graph and generates an RDF-ID for the node. """
        self.id = URIRef(graph.getCNS() + id)
        self.graph = graph

    def label(self, label: str):
        """ provides a human readable label for the node via rdfs:label

        Parameters
        ----------
        label: str
        """
        self.graph.add((self.id, RDFS.label, Literal(label)))

    def description(self, description: str):
        """ provides a detailed description of the node via rdfs:comment.
        https://www.w3.org/TR/rdf-schema/#ch_comment

        Parameters
        ----------
        description: str    
        """
        self.graph.add((self.id, RDFS.comment, Literal(description)))

    def getId(self):
        """ 
        Returns
        -------
        self.id: rdflib.URIRef
            RDF-ID of the node        
        """
        return self.id


class Activity(Node):
    """ Class to instantiate a PROV-O Activity object. 
    https://www.w3.org/TR/prov-o/#Activity
    The methods reflect the properties of an Activity.
    
    Parameters
    ----------
    graph: ProvGraph
        The graph to which the node should be added.
    id: str
        The ID of the node. The ID has to be unique inside the custom 
        namespace of the ProvGraph instance. The ID also has to be 
        alphanumerical, without empty spaces.
    """
    def __init__(self, graph, id):
        """constructor: adds the node via RDF-ID as prov:Activity to the graph"""
        super().__init__(graph = graph, id = id)
        self.graph.add((self.id, RDF.type, PROV.Activity))

    def wasInformedBy(self, activity):
        """ implements the wasInformedBy property of PROV-O
        https://www.w3.org/TR/prov-o/#wasInformedBy


        Parameters
        ----------
        activity: Activity
            The Activity that informed this Activity.        
        """
        assert(isinstance(activity, Activity))
        self.graph.add((self.id, PROV.wasInformedBy, activity.getId()))

    def used(self, entity):
        """ implements the used property of PROV-O
        https://www.w3.org/TR/prov-o/#used


        Parameters
        ----------
        entity: Entity
            The Entity that was used by this Activity.
        """
        assert(isinstance(entity, Entity))
        self.graph.add((self.id, PROV.used, entity.getId()))

    def wasAssociatedWith(self, agent):
        """ implements the wasAssociatedWith property of PROV-O
        https://www.w3.org/TR/prov-o/#wasAssociatedWith


        Parameters
        ----------
        agent: Agent
            The Agent that this Activity was assciated with. 
        """
        assert(isinstance(agent, Agent))
        self.graph.add((self.id, PROV.wasAssociatedWith, agent.getId()))

    def startedAtTime(self, datetime_in: datetime):
        """ implements the startedAtTime property of PROV-O
        https://www.w3.org/TR/prov-o/#startedAtTime


        Parameters
        ----------
        datetime_in: datetime.datetime
            The time a which this Activity started.
        """
        assert(isinstance(datetime_in, datetime))
        self.graph.add((self.id, PROV.startedAtTime, Literal(datetime_in, datatype = XSD.datetime)))
    
    def endedAtTime(self, datetime_in: datetime):
        """ implements the endedAtTime property of PROV-O
        https://www.w3.org/TR/prov-o/#endedAtTime


        Parameters
        ----------
        datetime_in: datetime.datetime
            The time a which this Activity ended.
        """
        assert(isinstance(datetime_in, datetime))
        self.graph.add((self.id, PROV.endedAtTime, Literal(datetime_in, datatype = XSD.datetime)))


class Entity(Node):
    """ Class to instantiate a PROV-O Entity object. 
    https://www.w3.org/TR/prov-o/#Entity
    The methods reflect the properties of an Entity.

    Parameters
    ----------
    graph: ProvGraph
        The graph to which the node should be added.
    id: str
        The ID of the node. The ID has to be unique inside the custom 
        namespace of the ProvGraph instance. The ID also has to be 
        alphanumerical, without empty spaces.
    """
    def __init__(self, graph, id):
        """constructor: adds the node via RDF-ID as prov:Entity to the graph"""
        super().__init__(graph = graph, id = id)
        self.graph.add((self.id, RDF.type, PROV.Entity))
    
    def wasDerivedFrom(self, entity):
        """ implements the wasDerivedFrom property of PROV-O
        https://www.w3.org/TR/prov-o/#wasDerivedFrom


        Parameters
        ----------
        entity: Entity
            The Entity that this Entity was derived from.
        """
        assert(isinstance(entity, Entity))
        self.graph.add((self.id, PROV.wasDerivedFrom, entity.getId()))

    def wasGeneratedBy(self, activity):
        """ implements the wasGeneratedBy property of PROV-O
        https://www.w3.org/TR/prov-o/#wasgeneratedBy

        Parameters
        ----------
        activity: Activity
            The Activity that generated this Activity.
        """
        assert(isinstance(activity, Activity))
        self.graph.add((self.id, PROV.wasGeneratedBy, activity.getId()))

    def wasAttributedTo(self, agent):
        """ implements the wasAttributedTo property of PROV-O
        https://www.w3.org/TR/prov-o/#wasAttributedTo


        Parameters
        ----------
        agent: Agent
            The Agent that this Entity was attributed to.
        """
        assert(isinstance(agent, Agent))
        self.graph.add((self.id, PROV.wasAttributedTo, agent.getId()))
    
class Agent(Node):
    """ Class to instantiate a PROV-O Agent object. 
    https://www.w3.org/TR/prov-o/#Agent
    The methods reflect the properties of an Agent.

    Parameters
    ----------
    graph: ProvGraph
        The graph to which the node should be added.
    id: str
        The ID of the node. The ID has to be unique inside the custom 
        namespace of the ProvGraph instance. The ID also has to be 
        alphanumerical, without empty spaces.
    """
    def __init__(self, graph, id):
        """constructor: adds the node via RDF-ID as prov:Agent to the graph"""
        super().__init__(graph = graph, id = id)
        self.graph.add((self.id, RDF.type, PROV.Agent))

    def actedOnBehalfOf(self, agent):
        """ implements the actedOnBehalfOf property of PROV-O
        https://www.w3.org/TR/prov-o/#actedOnBehalfOf


        Parameters
        ----------
        agent: Agent
            The Agent instructed this Agent.  
        """
        assert(isinstance(agent, Agent))
        self.graph.add((self.id, PROV.actedOnBehalfOf, agent.getId()))
