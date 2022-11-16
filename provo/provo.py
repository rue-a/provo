"""
@author Arne Rümmler
@contact arne.ruemmler@gmail.com

@summary Implementation of the starting term classes of
 PROV-O https://www.w3.org/TR/prov-o/ .
@status Prototype
"""

from abc import ABC
from dataclasses import dataclass, field

from datetime import datetime
from uuid import uuid4


@dataclass(frozen=True)
class IdAlreadyUsedError(Exception):
    """Raised when a node with an id that already exists is created."""

    message: str


@dataclass
class IdVault:
    """manages unique IDs and generates new ones"""

    vault: list[str] = field(init=False, default_factory=list)

    def generate(self, namespace: str) -> str:
        """generates a new uuid that is not in the vault yet"""
        node_id = namespace + str(uuid4())
        while node_id in self.vault:
            node_id = namespace + str(uuid4())
        self.vault.append(node_id)
        return node_id

    def add_id(self, namespace: str, id: str) -> str:
        """adds a user defined id or generates a random id, if id is already used"""
        node_id = namespace + id
        if node_id in self.vault:
            raise IdAlreadyUsedError(f'The Id "{node_id}" was already used in this graph.')
        self.vault.append(node_id)
        return node_id


@dataclass
class Node(ABC):
    """ Abstract parent class of Activity, Agent, and Entity. """

    label: str = None
    description: str = None
    node_id: str = None


@dataclass
class Activity(Node):
    """ Class to create a PROV-O Activity object.
    https://www.w3.org/TR/prov-o/#Activity """

    was_informed_by_activities: list('Activity') = field(init=False, default_factory=list)
    used_entities: list('Entity') = field(init=False, default_factory=list)
    was_associated_with_agents: list('Agent') = field(init=False, default_factory=list)
    start_time: datetime = field(init=False)
    end_time: datetime = field(init=False)

    def was_informed_by(self, activity: 'Activity') -> None:
        """ implements the wasInformedBy property of PROV-O
        https://www.w3.org/TR/prov-o/#wasInformedBy """

        assert isinstance(activity, Activity)
        self.was_informed_by_activities.append(activity)

    def used(self, entity: 'Entity') -> None:
        """ implements the used property of PROV-O
        https://www.w3.org/TR/prov-o/#used """

        assert isinstance(entity, Entity)
        self.used_entities.append(entity)

    def was_associated_with(self, agent: 'Agent') -> None:
        """ implements the wasAssociatedWith property of PROV-O
        https://www.w3.org/TR/prov-o/#wasAssociatedWith """

        assert isinstance(agent, Agent)
        self.was_associated_with_agents.append(agent)

    def started_at_time(self, start_time: datetime) -> None:
        """ implements the startedAtTime property of PROV-O
        https://www.w3.org/TR/prov-o/#startedAtTime """

        assert isinstance(start_time, datetime)
        self.start_time = start_time

    def ended_at_time(self, end_time: datetime) -> None:
        """ implements the endedAtTime property of PROV-O
        https://www.w3.org/TR/prov-o/#endedAtTime """

        assert isinstance(end_time, datetime)
        self.end_time = end_time


@dataclass
class Entity(Node):
    """ Class to create a PROV-O Entity object. 
    https://www.w3.org/TR/prov-o/#Entity """

    was_derived_from_entities: list('Entity') = field(init=False, default_factory=list)
    was_generated_by_activities: list('Activity') = field(init=False, default_factory=list)
    was_attributed_to_agents: list('Agent') = field(init=False, default_factory=list)

    def was_derived_from(self, entity: 'Entity') -> None:
        """ implements the wasDerivedFrom property of PROV-O
        https://www.w3.org/TR/prov-o/#wasDerivedFrom """

        assert isinstance(entity, Entity)
        self.was_derived_from_entities.append(entity)

    def was_generated_by(self, activity: 'Activity') -> None:
        """ implements the wasGeneratedBy property of PROV-O
        https://www.w3.org/TR/prov-o/#wasgeneratedBy """

        assert isinstance(activity, Activity)
        self.was_generated_by_activities.append(activity)

    def was_attributed_to(self, agent: 'Agent') -> None:
        """ implements the wasAttributedTo property of PROV-O
        https://www.w3.org/TR/prov-o/#wasAttributedTo """

        assert isinstance(agent, Agent)
        self.was_attributed_to_agents.append(agent)


@dataclass
class Agent(Node):
    """ Class to create a PROV-O Agent object.
    https://www.w3.org/TR/prov-o/#Agent """

    acted_on_behalf_of_agents: list('Agent') = field(init=False, default_factory=list)

    def acted_on_behalf_of(self, agent: 'Agent') -> None:
        """ implements the actedOnBehalfOf property of PROV-O
        https://www.w3.org/TR/prov-o/#actedOnBehalfOf """

        assert isinstance(agent, Agent)
        self.acted_on_behalf_of_agents.append(agent)
