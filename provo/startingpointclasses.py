"""
@author Arne Rümmler
@contact arne.ruemmler@gmail.com

@summary Implementation of the starting term classes of
 PROV-O https://www.w3.org/TR/prov-o/ .
"""


from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class InvalidProvClassForThisRelation(Exception):
    """Raised when the wrong class is given as attribute
    to one of the starting point property methods."""

    message: str


@dataclass(frozen=True)
class NoDateTime(Exception):
    """Raised when no datetime object is given as attribute."""

    message: str


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

    def get_id(self) -> str:
        """returns the node's id"""

        return self.node_id

    def get_label(self) -> str:
        """returns the node's label"""

        return self.label

    def get_description(self) -> str:
        """returns the node's description"""

        return self.description


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

        if not isinstance(entity, Entity):
            raise InvalidProvClassForThisRelation(
                f"""The PROV relation "was derived from" refers to an Entity, thus the provided
                attribute has to be of type <class 'provo.startingpointclasses.Entity'>. 
                In contradiction to this, the provided attribute is of the type {type(entity)}."""
            )
        self._was_derived_from_entities.append(entity)

    def was_generated_by(self, activity: 'Activity') -> None:
        """ implements the wasGeneratedBy property of PROV-O
        https://www.w3.org/TR/prov-o/#wasgeneratedBy """

        if not isinstance(activity, Activity):
            raise InvalidProvClassForThisRelation(
                f"""The PROV relation "was generated by" refers to an Activity, thus the provided
                attribute has to be of type <class 'provo.startingpointclasses.Activity'>. 
                In contradiction to this, the provided attribute is of the type {type(activity)}."""
            )
        self._was_generated_by_activities.append(activity)

    def was_attributed_to(self, agent: 'Agent') -> None:
        """ implements the wasAttributedTo property of PROV-O
        https://www.w3.org/TR/prov-o/#wasAttributedTo """

        if not isinstance(agent, Agent):
            raise InvalidProvClassForThisRelation(
                f"""The PROV relation "was attributed to" refers to an Agent, thus the provided
                attribute has to be of type <class 'provo.startingpointclasses.Agent'>. 
                In contradiction to this, the provided attribute is of the type {type(agent)}."""
            )
        self._was_attributed_to_agents.append(agent)


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

        if not isinstance(activity, Activity):
            raise InvalidProvClassForThisRelation(
                f"""The PROV relation "was informed by" refers to an Activity, thus the provided
                attribute has to be of type <class 'provo.startingpointclasses.Activity'>. 
                In contradiction to this, the provided attribute is of the type {type(activity)}."""
            )
        self._was_informed_by_activities.append(activity)

    def used(self, entity: 'Entity') -> None:
        """ implements the used property of PROV-O
        https://www.w3.org/TR/prov-o/#used """

        if not isinstance(entity, Entity):
            raise InvalidProvClassForThisRelation(
                f"""The PROV relation "used" refers to an Entity, thus the provided
                attribute has to be of type <class 'provo.startingpointclasses.Entity'>. 
                In contradiction to this, the provided attribute is of the type {type(entity)}."""
            )
        self._used_entities.append(entity)

    def was_associated_with(self, agent: 'Agent') -> None:
        """ implements the wasAssociatedWith property of PROV-O
        https://www.w3.org/TR/prov-o/#wasAssociatedWith """

        if not isinstance(agent, Agent):
            raise InvalidProvClassForThisRelation(
                f"""The PROV relation "was associated with" refers to an Agent, thus the provided
                attribute has to be of type <class 'provo.startingpointclasses.Agent'>. 
                In contradiction to this, the provided attribute is of the type {type(agent)}."""
            )
        self._was_associated_with_agents.append(agent)

    def started_at_time(self, start_time: datetime) -> None:
        """ implements the startedAtTime property of PROV-O
        https://www.w3.org/TR/prov-o/#startedAtTime """

        if not isinstance(start_time, datetime):
            raise NoDateTime("The attribute `start_time` of the method `started_at_time` has to be a `datetime` object.")
        self._start_time = start_time

    def ended_at_time(self, end_time: datetime) -> None:
        """ implements the endedAtTime property of PROV-O
        https://www.w3.org/TR/prov-o/#endedAtTime """

        if not isinstance(end_time, datetime):
            raise NoDateTime("The attribute `end_time` of the method `ended_at_time` has to be a `datetime` object.")

        self._end_time = end_time


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

        if not isinstance(agent, Agent):
            raise InvalidProvClassForThisRelation(
                f"""The PROV relation "acted on behalf of" refers to an Agent, thus the provided
                attribute has to be of type <class 'provo.startingpointclasses.Agent'>. 
                In contradiction to this, the provided attribute is of the type {type(agent)}."""
            )
        self._acted_on_behalf_of_agents.append(agent)
