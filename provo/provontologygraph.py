"""
@author Arne Rümmler
@contact arne.ruemmler@gmail.com

@summary Implementation of a provenance graph
    class that uses PROV-O terms
"""


from dataclasses import dataclass, field

from rdflib import (DC, FOAF, PROV, RDF, RDFS, XSD, Graph,  # type: ignore
                    Literal, Namespace, URIRef)
from validators import url

from provo.idvault import IdVault
from provo.startingpointclasses import Activity, Agent, Entity
from provo.staticfunctions import update_dict


@dataclass(frozen=True)
class NamespaceMalformed(Exception):
    """Raised when the namespace is not a valid URL."""

    message: str


@dataclass(frozen=True)
class NamespaceHasNoEndSymbol(Exception):
    """Raised if the namespace does not end with '/' or '#'."""

    message: str


@dataclass(frozen=True)
class PrefixShorthandNotValid(Exception):
    """Raised if the namespace abbreviation contains non-allowed characters."""

    message: str


@dataclass(frozen=True)
class PrefixNotAllowed(Exception):
    """Raised the namespace is not allowed."""

    message: str


@dataclass
class ProvOntologyGraph():
    """model that manages contents of a provenance graph
    that adheres to the PROV-O provenance model."""

    namespace: str = "https://provo-example.org/"
    namespace_abbreviation: str = ""
    lang: str = "en"
    _entities: list[Entity] = field(init=False, default_factory=list)
    _activities: list[Activity] = field(init=False, default_factory=list)
    _agents: list[Agent] = field(init=False, default_factory=list)
    _id_vault: IdVault = field(init=False, default_factory=IdVault)

    def __post_init__(self):
        """check validity of namespace and and namespace abbreviation"""

        # validate namespace
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

        # validate namespace abbreviation
        # TODO check what is actually allowed
        allowed_symbols_for_prefix_shorthand = 'abcdefghijklmnopqrstuvwxyz'

        for symbol in self.namespace_abbreviation:
            if symbol not in allowed_symbols_for_prefix_shorthand:
                raise PrefixShorthandNotValid(f"""
                    The provided namespace abbreviation is not valid.
                    
                    Character of the namespace have to be in "{allowed_symbols_for_prefix_shorthand}".
                    """)
        # if self.namespace_abbreviation in forbidden_namespaces:
        core_prefixes = ["owl", "rdf", "rdfs", "xsd", "xml"]
        if self.namespace_abbreviation in core_prefixes:
            raise PrefixNotAllowed(f"""
            The provided namespace abbreviation is a core prefix, 
            and thus, prohibited from use.

            Core prefixes are: {"".join([f"{k}, " if i != len(core_prefixes)-2 else f"{k} and " for i, k in enumerate(core_prefixes)])[:-2]}.
            """)

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

    def _handle_id(self, namespace: str = "", id_string: str = "") -> str:
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

    def add_entity(self, id_string: str = "", label: str = "", description: str = "", namespace: str = "") -> Entity:
        """creates a new entity, adds it to the graph and returns it then"""

        node_id = self._handle_id(namespace, id_string)
        entity = Entity(
            node_id=node_id,
            label=label,
            description=description)
        self._entities.append(entity)
        return entity

    def add_activity(self, id_string: str = "", label: str = "", description: str = "", namespace: str = "") -> Activity:
        """creates a new activity, adds it to the graph and returns it then"""

        node_id = self._handle_id(namespace, id_string)
        activity = Activity(
            node_id=node_id,
            label=label,
            description=description)
        self._activities.append(activity)
        return activity

    def add_agent(self, id_string: str = "", label: str = "", description: str = "", namespace: str = "") -> Agent:
        """creates a new agent, adds it to the graph and returns it then"""

        node_id = self._handle_id(namespace, id_string)
        agent = Agent(
            node_id=node_id,
            label=label,
            description=description)
        self._agents.append(agent)
        return agent

    # TODO
    # def read_graph(self, file_path: str) -> None:
    #     """reads the contents of an existing PROV-O provenance graph."""

    #     pass

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
                    URIRef(node.node_id), RDFS.label, Literal(node.label, lang=self.lang)
                ))
            if node.description:
                provenance_graph.add((
                    URIRef(node.node_id), RDFS.comment, Literal(node.description, lang=self.lang)
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

    def export_as_mermaid_flowchart(self, file_name: str, user_options: dict = {}) -> None:
        """exports the contents of the graph as mermaid-md flowchart"""

        # if possible the options use the mermaid terminology
        options = {
            "revert-relations": False,
            "orientation": "TD",            
            "included-relations": [
                "was_generated_by",
                "was_attributed_to",
                "used",
                "was_associated_with",
                "acted_on_behalf_of"
            ],
            "color": "#000000",
            "stroke": "#a4a4a4",
            "stroke-width": "1px",
            "relation-style": "-",
            "entity": {
                "fill": "#fffedf",
                "shape": "([:])",
                "relation-style": None,
                "color": None,
                "stroke": None,
                "stroke-width": None
            },
            "activity": {
                "fill": "#cfceff",
                "shape": "[[:]]",
                "relation-style": None,
                "color": None,
                "stroke": None,
                "stroke-width": None
            },
            "agent": {
                "fill": "#ffebc3",
                "shape": "[/:\\]",
                "relation-style": ".",
                "color": None,
                "stroke":  None,
                "stroke-width": None
            }
        }

        options = update_dict(options, user_options)

        text_color = options["color"]
        stroke_color = options["stroke"]
        stroke_width = options["stroke-width"]
        stroke_style = options["relation-style"]

        entity_text_color = options["entity"]["color"]
        entity_stroke_color = options["entity"]["stroke"]
        entity_stroke_width = options["entity"]["stroke-width"]
        entity_stroke_style = options["entity"]["relation-style"]

        activity_text_color = options["activity"]["color"]
        activity_stroke_color = options["activity"]["stroke"]
        activity_stroke_width = options["activity"]["stroke-width"]
        activity_stroke_style = options["activity"]["relation-style"]

        agent_text_color = options["agent"]["color"]
        agent_stroke_color = options["agent"]["stroke"]
        agent_stroke_width = options["agent"]["stroke-width"]
        agent_stroke_style = options["agent"]["relation-style"]

        lines = []
        lines.append("```mermaid")
        lines.append(f"flowchart {options['orientation']}")

        lines.append(f"classDef entity fill:{options['entity']['fill']}")
        if entity_text_color:
            lines.append(f"classDef entity color:{options['entity']['color']}")
        elif text_color:
            lines.append(f"classDef entity color:{options['color']}")
        if entity_stroke_color:
            lines.append(f"classDef entity stroke:{options['entity']['stroke']}")
        elif stroke_color:
            lines.append(f"classDef entity stroke:{options['stroke']}")
        if entity_stroke_width:
            lines.append(f"classDef entity stroke-width:{options['entity']['stroke-width']}")
        elif stroke_width:
            lines.append(f"classDef entity stroke-width:{options['stroke-width']}")

        lines.append(f"classDef activity fill:{options['activity']['fill']}")
        if activity_text_color:
            lines.append(f"classDef activity color:{options['activity']['color']}")
        elif text_color:
            lines.append(f"classDef activity color:{options['color']}")
        if activity_stroke_color:
            lines.append(f"classDef activity stroke:{options['activity']['stroke']}")
        elif stroke_color:
            lines.append(f"classDef activity stroke:{options['stroke']}")
        if activity_stroke_width:
            lines.append(f"classDef activity stroke-width:{options['activity']['stroke-width']}")
        elif stroke_width:
            lines.append(f"classDef activity stroke-width:{options['stroke-width']}")

        lines.append(f"classDef agent fill:{options['agent']['fill']}")
        if agent_text_color:
            lines.append(f"classDef agent color:{options['agent']['color']}")
        elif text_color:
            lines.append(f"classDef agent color:{options['color']}")
        if agent_stroke_color:
            lines.append(f"classDef agent stroke:{options['agent']['stroke']}")
        elif stroke_color:
            lines.append(f"classDef agent stroke:{options['stroke']}")
        if agent_stroke_width:
            lines.append(f"classDef agent stroke-width:{options['agent']['stroke-width']}")
        elif stroke_width:
            lines.append(f"classDef agent stroke-width:{options['stroke-width']}")

        for entity in self._entities:
            lines.append(
                f"{entity.get_id()}{options['entity']['shape'].split(':')[0]}{entity.get_label() if entity.get_label() else entity.get_id()}{options['entity']['shape'].split(':')[1]}:::entity")
            if "was_derived_by" in options["included-relations"]:
                for item in entity._was_derived_from_entities:
                    if not options["revert-relations"]:
                        lines.append(f"{entity.get_id()}-{entity_stroke_style if entity_stroke_style else stroke_style} was derived from {entity_stroke_style if entity_stroke_style else stroke_style}->{item.get_id()}")
                    else:
                        lines.append(f"{item.get_id()}-{entity_stroke_style if entity_stroke_style else stroke_style} originated from {entity_stroke_style if entity_stroke_style else stroke_style}->{entity.get_id()}")
            if "was_generated_by" in options["included-relations"]:
                for item in entity._was_generated_by_activities:
                    if not options["revert-relations"]:
                        lines.append(f"{entity.get_id()}-{activity_stroke_style if activity_stroke_style else stroke_style} was generated by {activity_stroke_style if activity_stroke_style else stroke_style}->{item.get_id()}")
                    else:
                        lines.append(f"{item.get_id()}-{activity_stroke_style if activity_stroke_style else stroke_style} generated {activity_stroke_style if activity_stroke_style else stroke_style}->{entity.get_id()}")
            if "was_attributed_to" in options["included-relations"]:
                for item in entity._was_attributed_to_agents:
                    if not options["revert-relations"]:
                        lines.append(f"{entity.get_id()}-{agent_stroke_style if agent_stroke_style else stroke_style} was attributed to {agent_stroke_style if agent_stroke_style else stroke_style}->{item.get_id()}")
                    else:
                        lines.append(f"{item.get_id()}-{agent_stroke_style if agent_stroke_style else stroke_style} produced {agent_stroke_style if agent_stroke_style else stroke_style}->{entity.get_id()}")

        for activity in self._activities:
            lines.append(
                f"{activity.get_id()}{options['activity']['shape'].split(':')[0]}{activity.get_label() if activity.get_label() else activity.get_id()}{options['activity']['shape'].split(':')[1]}:::activity")
            if "was_informed_by" in options["included-relations"]:
                for item in activity._was_informed_by_activities:
                    if not options["revert-relations"]:
                        lines.append(f"{activity.get_id()}-{entity_stroke_style if entity_stroke_style else stroke_style} was informed by {entity_stroke_style if entity_stroke_style else stroke_style}->{item.get_id()}")
                    else:
                        lines.append(f"{item.get_id()}-{entity_stroke_style if entity_stroke_style else stroke_style} informed {entity_stroke_style if entity_stroke_style else stroke_style}->{activity.get_id()}")
            if "used" in options["included-relations"]:
                for item in activity._used_entities:
                    if not options["revert-relations"]:
                        lines.append(f"{activity.get_id()}-{activity_stroke_style if activity_stroke_style else stroke_style} used {activity_stroke_style if activity_stroke_style else stroke_style}->{item.get_id()}")
                    else:
                        lines.append(f"{item.get_id()}-{activity_stroke_style if activity_stroke_style else stroke_style} was used by {activity_stroke_style if activity_stroke_style else stroke_style}->{activity.get_id()}")
            if "was_associated_with" in options["included-relations"]:
                for item in activity._was_associated_with_agents:
                    if not options["revert-relations"]:
                        lines.append(f"{activity.get_id()}-{agent_stroke_style if agent_stroke_style else stroke_style} was associated with {agent_stroke_style if agent_stroke_style else stroke_style}->{item.get_id()}")
                    else:
                        lines.append(f"{item.get_id()}-{agent_stroke_style if agent_stroke_style else stroke_style} initiated {agent_stroke_style if agent_stroke_style else stroke_style}->{activity.get_id()}")

        for agent in self._agents:
            lines.append(f"{agent.get_id()}{options['agent']['shape'].split(':')[0]}{agent.get_label() if agent.get_label() else agent.get_id()}{options['agent']['shape'].split(':')[1]}:::agent")
            if "acted_on_behalf_of" in options["included-relations"]:
                for item in agent._acted_on_behalf_of_agents:
                    if not options["revert-relations"]:
                        lines.append(f"{agent.get_id()}-{agent_stroke_style if agent_stroke_style else stroke_style} acted on behalf of {agent_stroke_style if agent_stroke_style else stroke_style}->{item.get_id()}")
                    else:
                        lines.append(f"{item.get_id()}-{agent_stroke_style if agent_stroke_style else stroke_style} instructed {agent_stroke_style if agent_stroke_style else stroke_style}->{agent.get_id()}")

        lines.append("```")
        lines = "\n".join(lines)

        with open(file_name, "w") as f:
            f.write(lines)
