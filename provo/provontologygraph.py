"""
@author Arne Rümmler
@contact arne.ruemmler@gmail.com

@summary Implementation of a provenance graph
    class that uses PROV-O terms
"""


from dataclasses import dataclass, field

from rdflib import (
    DC,
    FOAF,
    PROV,
    RDF,
    RDFS,
    XSD,
    Graph,  # type: ignore
    Literal,
    Namespace,
    URIRef,
)
from validators import url

from provo.idvault import IdVault
from provo.startingpointclasses import Activity, Agent, Entity
from provo.staticfunctions import update_dict, get_option


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
class ProvOntologyGraph:
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
        # TODO rethink validation, we technically want to validate an IRI
        if not url(self.namespace):  # type: ignore
            raise NamespaceMalformed(
                """
            The provided namespace is not a valid URL!

            See validators package (https://github.com/python-validators/validators),
            validators.url() or https://gist.github.com/dperini/729294 for more
            information on what qualifies a URL as valid.
            
            https://www.rfc-editor.org/rfc/rfc3986#section-3:
            3.  Syntax Components

            The generic URI syntax consists of a hierarchical sequence of
            components referred to as the scheme, authority, path, query, and
            fragment.

                URI         = scheme ":" hier-part [ "?" query ] [ "#" fragment ]

                hier-part   = "//" authority path-abempty
                            / path-absolute
                            / path-rootless
                            / path-empty

            The scheme and path components are required, though the path may be
            empty (no characters).  When authority is present, the path must
            either be empty or begin with a slash ("/") character.  When
            authority is not present, the path cannot begin with two slash
            characters ("//").  These restrictions result in five different ABNF
            rules for a path (Section 3.3), only one of which will match any
            given URI reference.

            The following are two example URIs and their component parts:

                    foo://example.com:8042/over/there?name=ferret#nose
                    \_/   \______________/\_________/ \_________/ \__/
                    |           |            |            |        |
                scheme     authority       path        query   fragment
                    |   _____________________|__
                    / \ /                        \
                    urn:example:animal:ferret:nose
            """
            )
        end_symbol = self.namespace[-1]
        if end_symbol not in ("/", "#"):
            raise NamespaceHasNoEndSymbol(
                "The provided Namespace has to end on a '/' or '#'!"
            )

        # validate namespace abbreviation
        # TODO check what is actually allowed
        allowed_symbols_for_prefix_shorthand = "abcdefghijklmnopqrstuvwxyz"

        for symbol in self.namespace_abbreviation:
            if symbol not in allowed_symbols_for_prefix_shorthand:
                raise PrefixShorthandNotValid(
                    f"""
                    The provided namespace abbreviation is not valid.
                    
                    Character of the namespace have to be in "{allowed_symbols_for_prefix_shorthand}".
                    """
                )
        # if self.namespace_abbreviation in forbidden_namespaces:
        core_prefixes = ["owl", "rdf", "rdfs", "xsd", "xml"]
        if self.namespace_abbreviation in core_prefixes:
            raise PrefixNotAllowed(
                f"""
            The provided namespace abbreviation is a core prefix, 
            and thus, prohibited from use.

            Core prefixes are: {"".join([f"{k}, " if i != len(core_prefixes)-2 else f"{k} and " for i, k in enumerate(core_prefixes)])[:-2]}.
            """
            )

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

    def _handle_id(self, id: str = "", use_namespace: bool = False) -> str:
        """checks whether the provided namespace-id combination is
        already used for a node in the graph.
        if no namespace is provided: default namespace is used,
        if no id is provided: id get automatically generated."""

        if use_namespace:
            id = self.namespace + id
        if id:
            node_id = self._id_vault.add_id(id)
        else:
            node_id = self._id_vault.generate(self.namespace)
        return node_id

    def add_entity(
        self,
        id: str = "",
        label: str = "",
        description: str = "",
        use_namespace: bool = False,
    ) -> Entity:
        """creates a new entity, adds it to the graph and returns it then"""

        node_id = self._handle_id(id, use_namespace)
        entity = Entity(node_id=node_id, label=label, description=description)
        self._entities.append(entity)
        return entity

    def add_activity(
        self,
        id: str = "",
        label: str = "",
        description: str = "",
        use_namespace: bool = False,
    ) -> Activity:
        """creates a new activity, adds it to the graph and returns it then"""

        node_id = self._handle_id(id, use_namespace)
        activity = Activity(node_id=node_id, label=label,
                            description=description)
        self._activities.append(activity)
        return activity

    def add_agent(
        self,
        id: str = "",
        label: str = "",
        description: str = "",
        use_namespace: bool = False,
    ) -> Agent:
        """creates a new agent, adds it to the graph and returns it then"""

        node_id = self._handle_id(id, use_namespace)
        agent = Agent(node_id=node_id, label=label, description=description)
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
        provenance_graph.bind(self.namespace_abbreviation,
                              Namespace(self.namespace))

        for node in self._entities + self._activities + self._agents:
            if node.label:
                provenance_graph.add(
                    (
                        URIRef(node.node_id),
                        RDFS.label,
                        Literal(node.label, lang=self.lang),
                    )
                )
            if node.description:
                provenance_graph.add(
                    (
                        URIRef(node.node_id),
                        RDFS.comment,
                        Literal(node.description, lang=self.lang),
                    )
                )
        for entity in self._entities:
            provenance_graph.add(
                (URIRef(entity.node_id), RDF.type, PROV.Entity))
            for activity in entity._was_generated_by_activities:
                provenance_graph.add(
                    (
                        URIRef(entity.node_id),
                        PROV.wasGeneratedBy,
                        URIRef(activity.node_id),
                    )
                )
            for origin_entity in entity._was_derived_from_entities:
                provenance_graph.add(
                    (
                        URIRef(entity.node_id),
                        PROV.wasDerivedFrom,
                        URIRef(origin_entity.node_id),
                    )
                )
            for agent in entity._was_attributed_to_agents:
                provenance_graph.add(
                    (
                        URIRef(entity.node_id),
                        PROV.wasAttributedTo,
                        URIRef(agent.node_id),
                    )
                )
        for activity in self._activities:
            provenance_graph.add(
                (URIRef(activity.node_id), RDF.type, PROV.Activity))
            if activity._start_time:
                provenance_graph.add(
                    (
                        URIRef(activity.node_id),
                        PROV.startedAtTime,
                        Literal(activity._start_time, datatype=XSD.dateTime),
                    )
                )
            if activity._end_time:
                provenance_graph.add(
                    (
                        URIRef(activity.node_id),
                        PROV.endedAtTime,
                        Literal(activity._end_time, datatype=XSD.dateTime),
                    )
                )
            for entity in activity._used_entities:
                provenance_graph.add(
                    (URIRef(activity.node_id), PROV.used, URIRef(entity.node_id))
                )
            for previous_activity in activity._was_informed_by_activities:
                provenance_graph.add(
                    (
                        URIRef(activity.node_id),
                        PROV.wasInformedBy,
                        URIRef(previous_activity.node_id),
                    )
                )
            for agent in activity._was_associated_with_agents:
                provenance_graph.add(
                    (
                        URIRef(agent.node_id),
                        PROV.wasAssociatedWith,
                        URIRef(agent.node_id),
                    )
                )
        for agent in self._agents:
            provenance_graph.add((URIRef(agent.node_id), RDF.type, PROV.Agent))
            for instructor in agent._acted_on_behalf_of_agents:
                provenance_graph.add(
                    (
                        URIRef(agent.node_id),
                        PROV.actedOnBehalfOf,
                        URIRef(instructor.node_id),
                    )
                )

        return provenance_graph

    def serialize_as_rdf(self, file_name: str, export_format: str = "turtle") -> None:
        """serializes the graph as rdf, available formats are:
        "xml", "n3", "turtle", "nt", "pretty-xml", "trix", "trig", "nquads", "json-ld", "hext"
        """
        self.get_rdflib_graph().serialize(destination=file_name, format=export_format)

    def export_as_mermaid_flowchart(
        self, file_name: str, user_options: dict = {}
    ) -> None:
        """exports the contents of the graph as mermaid-md flowchart"""

        # if possible the options use the mermaid terminology
        default_options = {
            "invert-relations": False,
            "orientation": "TD",
            "included-relations": [
                "was_generated_by",
                "was_attributed_to",
                "used",
                "was_associated_with",
                "acted_on_behalf_of",
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
                "stroke-width": None,
            },
            "activity": {
                "fill": "#cfceff",
                "shape": "[[:]]",
                "relation-style": None,
                "color": None,
                "stroke": None,
                "stroke-width": None,
            },
            "agent": {
                "fill": "#ffebc3",
                "shape": "[/:\\]",
                "relation-style": ".",
                "color": None,
                "stroke": None,
                "stroke-width": None,
            },
        }

         # Update default options with user options
        options = update_dict(default_options, user_options)

        # Unpack commonly used option values
        text_color = options["color"]
        stroke_color = options["stroke"]
        stroke_width = options["stroke-width"]
        stroke_style = options["relation-style"]

        # Unpack entity options
        entity_opts = options["entity"]
        entity_fill_color = entity_opts["fill"]
        entity_text_color = entity_opts["color"] or text_color
        entity_stroke_color = entity_opts["stroke"] or stroke_color
        entity_stroke_width = entity_opts["stroke-width"] or stroke_width
        entity_stroke_style = entity_opts["relation-style"] or stroke_style

        # Unpack activity options
        activity_opts = options["activity"]
        activity_fill_color = activity_opts["fill"]
        activity_text_color = activity_opts["color"] or text_color
        activity_stroke_color = activity_opts["stroke"] or stroke_color
        activity_stroke_width = activity_opts["stroke-width"] or stroke_width
        activity_stroke_style = activity_opts["relation-style"] or stroke_style

        # Unpack agent options
        agent_opts = options["agent"]
        agent_fill_color = agent_opts["fill"]
        agent_text_color = agent_opts["color"] or text_color
        agent_stroke_color = agent_opts["stroke"] or stroke_color
        agent_stroke_width = agent_opts["stroke-width"] or stroke_width
        agent_stroke_style = agent_opts["relation-style"] or stroke_style



        lines = []
        lines.append("```mermaid")
        lines.append(f"flowchart {options['orientation']}")

        # Class definitions for entities
        lines.append(f"classDef entity fill:{entity_fill_color}")
        if entity_text_color:
            lines.append(f"classDef entity color:{entity_text_color}")
        if entity_stroke_color:
            lines.append(f"classDef entity stroke:{entity_stroke_color}")
        if entity_stroke_width:
            lines.append(f"classDef entity stroke-width:{entity_stroke_width}")

        # Class definitions for activities
        lines.append(f"classDef activity fill:{activity_fill_color}")
        if activity_text_color:
            lines.append(f"classDef activity color:{activity_text_color}")
        if activity_stroke_color:
            lines.append(f"classDef activity stroke:{activity_stroke_color}")
        if activity_stroke_width:
            lines.append(f"classDef activity stroke-width:{activity_stroke_width}")

        # Class definitions for agents
        lines.append(f"classDef agent fill:{agent_fill_color}")
        if agent_text_color:
            lines.append(f"classDef agent color:{agent_text_color}")
        if agent_stroke_color:
            lines.append(f"classDef agent stroke:{agent_stroke_color}")
        if agent_stroke_width:
            lines.append(f"classDef agent stroke-width:{agent_stroke_width}")

        for entity in self._entities:
            lines.append(
                f'{entity.node_id}{options["entity"]["shape"].split(":")[0]}<a style=color:inherit href={entity.node_id}>{entity.label or entity.node_id}</a>{options["entity"]["shape"].split(":")[1]}:::entity'
            )
            if "was_derived_by" in options["included-relations"]:
                attrs = "style=color:inherit href=https://www.w3.org/TR/prov-o/#wasDerivedFrom"
                for item in entity._was_derived_from_entities:                    
                    if not options["invert-relations"]:
                        lines.append(
                            f"{entity.node_id}-{entity_stroke_style} <a {attrs}>was derived from</a> {entity_stroke_style}->{item.node_id}"
                        )
                    else:
                        lines.append(
                            f"{item.node_id}-{entity_stroke_style} <a {attrs}>originated from</a> {entity_stroke_style}->{entity.node_id}"
                        )
            if "was_generated_by" in options["included-relations"]:
                attrs ="style=color:inherit href=https://www.w3.org/TR/prov-o/#wasGeneratedBy"
                for item in entity._was_generated_by_activities:
                    
                    if not options["invert-relations"]:
                        lines.append(
                            f"{entity.node_id}-{activity_stroke_style} <a {attrs}>was generated by</a> {activity_stroke_style}->{item.node_id}"
                        )
                    else:
                        lines.append(
                            f"{item.node_id}-{activity_stroke_style} <a {attrs}>generated</a> {activity_stroke_style}->{entity.node_id}"
                        )
            if "was_attributed_to" in options["included-relations"]:
                attrs = "style=color:inherit href=https://www.w3.org/TR/prov-o/#wasAttributedTo"
                for item in entity._was_attributed_to_agents:
                    
                    if not options["invert-relations"]:
                        lines.append(
                            f"{entity.node_id}-{agent_stroke_style} <a {attrs}>was attributed to</a> {agent_stroke_style}->{item.node_id}"
                        )
                    else:
                        lines.append(
                            f"{item.node_id}-{agent_stroke_style} <a {attrs}>produced</a> {agent_stroke_style}->{entity.node_id}"
                        )

        for activity in self._activities:
            lines.append(
                f"{activity.node_id}{options['activity']['shape'].split(':')[0]}<a style=color:inherit href={activity.node_id}>{activity.label or activity.node_id}</a>{options['activity']['shape'].split(':')[1]}:::activity"
            )
            if "was_informed_by" in options["included-relations"]:
                attrs = "style=color:inherit href=https://www.w3.org/TR/prov-o/#wasInformedBy"
                for item in activity._was_informed_by_activities:
                    
                    if not options["invert-relations"]:
                        lines.append(
                            f"{activity.node_id}-{entity_stroke_style} <a {attrs}>was informed by</a> {entity_stroke_style}->{item.node_id}"
                        )
                    else:
                        lines.append(
                            f"{item.node_id}-{entity_stroke_style} <a {attrs}>informed</a> {entity_stroke_style}->{activity.node_id}"
                        )
            if "used" in options["included-relations"]:
                attrs="style=color:inherit href=https://www.w3.org/TR/prov-o/#used"
                for item in activity._used_entities:                    
                    if not options["invert-relations"]:
                        lines.append(
                            f"{activity.node_id}-{activity_stroke_style} <a {attrs}>used</a> {activity_stroke_style}->{item.node_id}"
                        )
                    else:
                        lines.append(
                            f"{item.node_id}-{activity_stroke_style} <a {attrs}>was used by</a> {activity_stroke_style}->{activity.node_id}"
                        )
            if "was_associated_with" in options["included-relations"]:
                attrs = "style=color:inherit href=https://www.w3.org/TR/prov-o/#wasAssociatedWith"
                for item in activity._was_associated_with_agents:
                    if not options["invert-relations"]:
                        lines.append(
                            f"{activity.node_id}-{agent_stroke_style} <a {attrs}>was associated with</a> {agent_stroke_style}->{item.node_id}"
                        )
                    else:
                        lines.append(
                            f"{item.node_id}-{agent_stroke_style} <a {attrs}>initiated</a> {agent_stroke_style}->{activity.node_id}"
                        )

        for agent in self._agents:
            lines.append(
                f"{agent.node_id}{options['agent']['shape'].split(':')[0]}<a style=color:inherit href={agent.node_id}>{agent.label or agent.node_id}</a>{options['agent']['shape'].split(':')[1]}:::agent"
            )
            if "acted_on_behalf_of" in options["included-relations"]:
                attrs = "style=color:inherit href=https://www.w3.org/TR/prov-o/#actedOnBehalfOf"
                for item in agent._acted_on_behalf_of_agents:
                    if not options["invert-relations"]:
                        lines.append(
                            f"{agent.node_id}-{agent_stroke_style} <a {attrs}>acted on behalf of</a> {agent_stroke_style}->{item.node_id}"
                        )
                    else:
                        lines.append(
                            f"{item.node_id}-{agent_stroke_style} <a {attrs}>instructed</a> {agent_stroke_style}->{agent.node_id}"
                        )

        lines.append("```")
        lines = "\n".join(lines)

        with open(file_name, "w", encoding="utf-8") as f:
            f.write(lines)
