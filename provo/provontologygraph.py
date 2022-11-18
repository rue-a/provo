"""
@author Arne Rümmler
@contact arne.ruemmler@gmail.com

@summary Implementation of a provenance graph
    class
@status Prototype
"""

from dataclasses import dataclass, field
from validators import url
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib import DC, FOAF, RDF, RDFS, PROV, XSD  # type: ignore

from .provo import IdVault, Entity, Activity, Agent


@dataclass(frozen=True)
class NamespaceMalformed(Exception):
    """Raised when the namespace is not a valid URL."""

    message: str


@dataclass(frozen=True)
class NamespaceHasNoEndSymbol(Exception):
    """Raise when the namespace does not end with '/' or '#'."""

    message: str


@dataclass
class ProvOntologyGraph():
    """model that manages contents of a provenance graph
    that adheres to the PROV-O provenance model."""

    namespace: str = "https://provo-example.org/"
    namespace_abbreviation: str = ""
    _entities: list[Entity] = field(init=False, default_factory=list)
    _activities: list[Activity] = field(init=False, default_factory=list)
    _agents: list[Agent] = field(init=False, default_factory=list)
    _id_vault: IdVault = field(init=False, default_factory=IdVault)

    def __post_init__(self):
        """check if the namespace is malformed"""
        # TODO rethink validation
        if not url(self.namespace):  # type: ignore
            raise NamespaceMalformed("""
            The provided namespace is not a valid URL!

            See validators package (https://github.com/python-validators/validators),
            validators.url() or https://gist.github.com/dperini/729294 for more
            information on what qualifies a URL as valid.""")
        end_symbol = self.namespace[-1]
        if end_symbol not in ('/', '#'):
            raise NamespaceHasNoEndSymbol("The provided Namespace has to end on a '/' or '#'!")

    def __handle_id(self, namespace: str = "", id_string: str = "") -> str:
        """checks whether the provided namespace-id combination is
        already used for a node in the graph.
        if no namespace is provided: default namespace is used,
        if no id is provided: id get automatically generated."""

        if not namespace:
            namespace = self.namespace
        if id_string:
            node_id = self._id_vault.add_id(namespace, id_string)
        else:
            node_id = self._id_vault.generate(namespace)
        return node_id

    def __str__(self) -> str:
        """prints the contents of the provenance graph in a nice format."""
        contents = "Provenance Graph Contents:"
        contents += "\n    ---"
        contents += "\n    Entities:"
        contents += "\n        ---\n"
        for entity in self._entities:
            lines = entity.__str__().splitlines()
            for line in lines:
                contents += f"        {line}\n"
        contents += "    ---"
        contents += "\n    Activities:"
        contents += "\n        ---\n"
        for activity in self._activities:
            lines = activity.__str__().splitlines()
            for line in lines:
                contents += f"        {line}\n"
        contents += "    ---"
        contents += "\n    Agents:"
        contents += "\n        ---\n"
        for agent in self._agents:
            lines = agent.__str__().splitlines()
            for line in lines:
                contents += f"        {line}\n"
        contents += "    ---"

        return contents

    def add_entity(self, id_string: str = "", label: str = "", description: str = "", namespace: str = "") -> Entity:
        """creates a new entity, adds it to the graph and returns it then"""

        node_id = self.__handle_id(namespace, id_string)
        entity = Entity(
            node_id=node_id,
            label=label,
            description=description)
        self._entities.append(entity)
        return entity

    def add_activity(self, id_string: str = "", label: str = "", description: str = "", namespace: str = "") -> Activity:
        """creates a new activity, adds it to the graph and returns it then"""

        node_id = self.__handle_id(namespace, id_string)
        activity = Activity(
            node_id=node_id,
            label=label,
            description=description)
        self._activities.append(activity)
        return activity

    def add_agent(self, id_string: str = "", label: str = "", description: str = "", namespace: str = "") -> Agent:
        """creates a new agent, adds it to the graph and returns it then"""

        node_id = self.__handle_id(namespace, id_string)
        agent = Agent(
            node_id=node_id,
            label=label,
            description=description)
        self._agents.append(agent)
        return agent

    def read_graph(self, file_path: str) -> None:
        """reads the contents of an existing PROV-O provenance graph."""
        pass

    def get_rdflib_graph(self) -> Graph:
        """returns the provenance graph as rdflib.Graph()."""

        provenance_graph = Graph()
        provenance_graph.bind("dc", DC)
        provenance_graph.bind("foaf", FOAF)
        provenance_graph.bind("rdf", RDF)
        provenance_graph.bind("rdfs", RDFS)
        provenance_graph.bind("prov", PROV)
        provenance_graph.bind(self.namespace_abbreviation, Namespace(self.namespace))

        for node in self._entities + self._activities + self._agents:
            if node.label:
                provenance_graph.add((
                    URIRef(node.node_id), RDFS.label, Literal(node.label)
                ))
            if node.description:
                provenance_graph.add((
                    URIRef(node.node_id), RDFS.comment, Literal(node.description)
                ))
        for entity in self._entities:
            provenance_graph.add((
                URIRef(entity.node_id), RDF.type, PROV.Entity
            ))
            for activity in entity._was_generated_by_activities:
                provenance_graph.add((
                    URIRef(entity.node_id), PROV.wasGeneratedBy, URIRef(activity.node_id)
                ))
            for origin_entity in entity._was_derived_from_entities:
                provenance_graph.add((
                    URIRef(entity.node_id), PROV.wasDerivedFrom, URIRef(origin_entity.node_id)
                ))
            for agent in entity._was_attributed_to_agents:
                provenance_graph.add((
                    URIRef(entity.node_id), PROV.wasAttributedTo, URIRef(agent.node_id)
                ))
        for activity in self._activities:
            provenance_graph.add((
                URIRef(activity.node_id), RDF.type, PROV.Activity
            ))
            if activity._start_time:
                provenance_graph.add((
                    URIRef(activity.node_id), PROV.startedAtTime, Literal(activity._start_time, datatype=XSD.dateTime)
                ))
            if activity._end_time:
                provenance_graph.add((
                    URIRef(activity.node_id), PROV.endedAtTime, Literal(activity._end_time, datatype=XSD.dateTime)
                ))
            for entity in activity._used_entities:
                provenance_graph.add((
                    URIRef(activity.node_id), PROV.used, URIRef(entity.node_id)
                ))
            for previous_activity in activity._was_informed_by_activities:
                provenance_graph.add((
                    URIRef(activity.node_id), PROV.wasInformedBy, URIRef(previous_activity.node_id)
                ))
            for agent in activity._was_associated_with_agents:
                provenance_graph.add((
                    URIRef(agent.node_id), PROV.wasAssociatedWith, URIRef(agent.node_id)
                ))
        for agent in self._agents:
            provenance_graph.add((
                URIRef(agent.node_id), RDF.type, PROV.Agent
            ))
            for instructor in agent._acted_on_behalf_of_agents:
                provenance_graph.add((
                    URIRef(agent.node_id), PROV.actedOnBehalfOf, URIRef(instructor.node_id)
                ))

        return provenance_graph

    def serialize_as_rdf(self, file_name: str, export_format: str = "turtle") -> None:
        """serializes the graph as rdf, available formats are:
        "xml", "n3", "turtle", "nt", "pretty-xml", "trix", "trig", "nquads", "json-ld", "hext"
        """
        self.get_rdflib_graph().serialize(destination=file_name, format=export_format)
