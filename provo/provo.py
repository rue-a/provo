"""
@author Arne Rümmler
@contact arne.ruemmler@gmail.com

@summary Implementation of the starting term classes of
 PROV-O https://www.w3.org/TR/prov-o/ .
@status Prototype
"""


from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass(frozen=True)
class IdInvalid(Exception):
    """Raised when a node id is invalid."""

    message: str


@dataclass(frozen=True)
class IdAlreadyUsed(Exception):
    """Raised when a node with an id that already exists is created."""

    message: str


@dataclass
class IdVault:
    """manages unique IDs and generates new ones"""

    vault: list[str] = field(init=False, default_factory=list)
    _invalid_symbols: str = field(init=False, default='<>" {}|\\^`')

    def uri_valid(self, uri: str) -> bool:
        "checks if uri is valid"

        for symbol in uri:
            if symbol in self._invalid_symbols:
                return False
        return True

    def generate(self, namespace: str) -> str:
        """generates a new uuid that is not in the vault yet"""
        node_id = namespace + str(uuid4())
        while node_id in self.vault:
            node_id = namespace + str(uuid4())
        if not self.uri_valid(node_id):
            raise IdInvalid(f"The Id {node_id} is invalid (contains one or more of: \033[1m{self._invalid_symbols}\033[0m).")
        self.vault.append(node_id)
        return node_id

    def add_id(self, namespace: str, id_string: str) -> str:
        """adds a user defined id and checks if its valid"""
        node_id = namespace + id_string
        if node_id in self.vault:
            raise IdAlreadyUsed(f'The Id "{node_id}" was already used in this graph.')
        if not self.uri_valid(node_id):
            raise IdInvalid(f"The Id {node_id} is invalid (contains one or more of: \033[1m{self._invalid_symbols}\033[0m).")
        self.vault.append(node_id)
        return node_id


@dataclass
class Node(ABC):
    """ Abstract parent class of Activity, Agent, and Entity. """

    label: str = ""
    description: str = ""
    node_id: str = ""

    @abstractmethod
    def __str__(self) -> str:
        """prints the node in a nice format"""
        contents = f"id: {self.node_id}"
        if self.label:
            contents += f"\nlabel: {self.label}"
        if self.description:
            contents += f"\ndescription: {self.description}"
        return contents


@dataclass
class Activity(Node):
    """ Class to create a PROV-O Activity object.
    https://www.w3.org/TR/prov-o/#Activity """

    _was_informed_by_activities: list['Activity'] = field(init=False, default_factory=list)
    _used_entities: list['Entity'] = field(init=False, default_factory=list)
    _was_associated_with_agents: list['Agent'] = field(init=False, default_factory=list)
    _start_time: datetime = field(init=False, default_factory=lambda: None)  # type: ignore (there is no default date that resolves to False)
    _end_time: datetime = field(init=False, default_factory=lambda: None)  # type: ignore

    def __str__(self) -> str:
        """prints the activity in a nice format."""
        contents = super().__str__()
        if self._start_time:
            contents += f"\nstart time: {self._start_time}"
        if self._end_time:
            contents += f"\nend time: {self._end_time}"
        if self._was_informed_by_activities:
            contents += f"\nwas informed by: {[item.label if item.label else item.node_id for item in self._was_informed_by_activities]}"
        if self._used_entities:
            contents += f"\nused: {[item.label if item.label else item.node_id for item in self._used_entities]}"
        if self._was_associated_with_agents:
            contents += f"\nwas associated with: {[item.label if item.label else item.node_id for item in self._was_associated_with_agents]}"
        contents += "\n---"
        return contents

    def was_informed_by(self, activity: 'Activity') -> None:
        """ implements the wasInformedBy property of PROV-O
        https://www.w3.org/TR/prov-o/#wasInformedBy """

        assert isinstance(activity, Activity)
        self._was_informed_by_activities.append(activity)

    def used(self, entity: 'Entity') -> None:
        """ implements the used property of PROV-O
        https://www.w3.org/TR/prov-o/#used """

        assert isinstance(entity, Entity)
        self._used_entities.append(entity)

    def was_associated_with(self, agent: 'Agent') -> None:
        """ implements the wasAssociatedWith property of PROV-O
        https://www.w3.org/TR/prov-o/#wasAssociatedWith """

        assert isinstance(agent, Agent)
        self._was_associated_with_agents.append(agent)

    def started_at_time(self, start_time: datetime) -> None:
        """ implements the startedAtTime property of PROV-O
        https://www.w3.org/TR/prov-o/#startedAtTime """

        assert isinstance(start_time, datetime)
        self._start_time = start_time

    def ended_at_time(self, end_time: datetime) -> None:
        """ implements the endedAtTime property of PROV-O
        https://www.w3.org/TR/prov-o/#endedAtTime """

        assert isinstance(end_time, datetime)
        self._end_time = end_time


@dataclass
class Entity(Node):
    """ Class to create a PROV-O Entity object. 
    https://www.w3.org/TR/prov-o/#Entity """

    _was_derived_from_entities: list['Entity'] = field(init=False, default_factory=list)
    _was_generated_by_activities: list['Activity'] = field(init=False, default_factory=list)
    _was_attributed_to_agents: list['Agent'] = field(init=False, default_factory=list)

    def __str__(self) -> str:
        """prints the entity in a nice format."""
        contents = super().__str__()
        if self._was_derived_from_entities:
            contents += f"\nwas derived from: {[item.label if item.label else item.node_id for item in self._was_derived_from_entities]}"
        if self._was_generated_by_activities:
            contents += f"\nwas generated by: {[item.label if item.label else item.node_id for item in self._was_generated_by_activities]}"
        if self._was_attributed_to_agents:
            contents += f"\nwas attributed to: {[item.label if item.label else item.node_id for item in self._was_attributed_to_agents]}"
        contents += "\n---"
        return contents

    def was_derived_from(self, entity: 'Entity') -> None:
        """ implements the wasDerivedFrom property of PROV-O
        https://www.w3.org/TR/prov-o/#wasDerivedFrom """

        assert isinstance(entity, Entity)
        self._was_derived_from_entities.append(entity)

    def was_generated_by(self, activity: 'Activity') -> None:
        """ implements the wasGeneratedBy property of PROV-O
        https://www.w3.org/TR/prov-o/#wasgeneratedBy """

        assert isinstance(activity, Activity)
        self._was_generated_by_activities.append(activity)

    def was_attributed_to(self, agent: 'Agent') -> None:
        """ implements the wasAttributedTo property of PROV-O
        https://www.w3.org/TR/prov-o/#wasAttributedTo """

        assert isinstance(agent, Agent)
        self._was_attributed_to_agents.append(agent)


@dataclass
class Agent(Node):
    """ Class to create a PROV-O Agent object.
    https://www.w3.org/TR/prov-o/#Agent """

    _acted_on_behalf_of_agents: list['Agent'] = field(init=False, default_factory=list)

    def __str__(self) -> str:
        """prints the agent in a nice format."""
        contents = super().__str__()
        if self._acted_on_behalf_of_agents:
            contents += f"\nacted on behalf of: {[item.label if item.label else item.node_id for item in self._acted_on_behalf_of_agents]}"
        contents += "\n---"
        return contents

    def acted_on_behalf_of(self, agent: 'Agent') -> None:
        """ implements the actedOnBehalfOf property of PROV-O
        https://www.w3.org/TR/prov-o/#actedOnBehalfOf """

        assert isinstance(agent, Agent)
        self._acted_on_behalf_of_agents.append(agent)
