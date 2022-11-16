"""
@author Arne Rümmler
@contact arne.ruemmler@gmail.com

@summary Implementation of a provenance graph
    class
@status Prototype
"""

from dataclasses import dataclass, field
from typing import Optional
from validators import url

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

    namespace: Optional[str] = 'https://provo-example.org/'
    entities: list[Entity] = field(init=False, default_factory=list)
    activities: list[Activity] = field(init=False, default_factory=list)
    agents: list[Agent] = field(init=False, default_factory=list)
    id_vault: IdVault = field(init=False, default_factory=IdVault)

    def __post_init__(self):
        """check if the namespace is malformed"""
        if not url(self.namespace):
            raise NamespaceMalformed("""
            The provided namespace is not a valid URL!
            
            See validators package (https://github.com/python-validators/validators),
            validators.url() or https://gist.github.com/dperini/729294 for more 
            information on what qualifies a URL as valid.""")
        end_symbol = self.namespace[-1]
        if not (end_symbol == "/" or end_symbol == "#"):
            raise NamespaceHasNoEndSymbol("The provided Namespace has to end on a '/' or '#'!")

    def __handle_id(self, namespace: str = "", id: str = "") -> str:
        """checks whether the provided namespace-id combination is 
        already used for a node in the graph. 
        if no namespace is provided: default namespace is used,
        if no id is provided: id get automatically generated."""

        if not namespace:
            namespace = self.namespace
        if id:
            node_id = self.id_vault.add_id(namespace, id)
        else:
            node_id = self.id_vault.generate(namespace)
        return node_id

    def new_entity(self, namespace: str = "", id: str = "", label: str = "", description: str = "") -> Entity:
        """creates a new entity, adds it to the graph and returns it then"""

        node_id = self.__handle_id(namespace, id)
        entity = Entity(
            node_id=node_id,
            label=label,
            description=description)
        self.entities.append(entity)
        return entity

    def new_activity(self, namespace: str = "", id: str = "", label: str = "", description: str = "") -> Activity:
        """creates a new activity, adds it to the graph and returns it then"""

        node_id = self.__handle_id(namespace, id)
        activity = Activity(
            node_id=node_id,
            label=label,
            description=description)
        self.activities.append(activity)
        return activity

    def new_agent(self, namespace: str = "", id: str = "", label: str = "", description: str = "") -> Agent:
        """creates a new activity, adds it to the graph and returns it then"""

        node_id = self.__handle_id(namespace, id)
        agent = Agent(
            node_id=node_id,
            label=label,
            description=description)
        self.agents.append(agent)
        return agent
