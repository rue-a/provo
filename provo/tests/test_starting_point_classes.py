from datetime import datetime

import pytest
from provo.startingpointclasses import (Activity, Agent, Entity,
                                        InvalidProvClassForThisRelation,
                                        NoDateTime)

entity = Entity(node_id='https://test.package/entity')
activity = Activity(node_id='https://test.package/activity')
agent = Agent(node_id='https://test.package/agent')


def test_was_derived_from():
    entity.was_derived_from(entity)
    with pytest.raises(InvalidProvClassForThisRelation):
        entity.was_derived_from(activity)  # type: ignore
    with pytest.raises(InvalidProvClassForThisRelation):
        entity.was_derived_from(agent)  # type: ignore


def test_was_generated_by():
    entity.was_generated_by(activity)
    with pytest.raises(InvalidProvClassForThisRelation):
        entity.was_generated_by(entity)  # type: ignore
    with pytest.raises(InvalidProvClassForThisRelation):
        entity.was_generated_by(agent)  # type: ignore


def test_was_attributed_to():
    entity.was_attributed_to(agent)
    with pytest.raises(InvalidProvClassForThisRelation):
        entity.was_attributed_to(activity)  # type: ignore
    with pytest.raises(InvalidProvClassForThisRelation):
        entity.was_attributed_to(entity)  # type: ignore


def test_was_informed_by():
    activity.was_informed_by(activity)
    with pytest.raises(InvalidProvClassForThisRelation):
        activity.was_informed_by(entity)  # type: ignore
    with pytest.raises(InvalidProvClassForThisRelation):
        activity.was_informed_by(agent)  # type: ignore


def test_was_associated_with():
    activity.was_associated_with(agent)
    with pytest.raises(InvalidProvClassForThisRelation):
        activity.was_associated_with(activity)  # type: ignore
    with pytest.raises(InvalidProvClassForThisRelation):
        activity.was_associated_with(entity)  # type: ignore


def test_used():
    activity.used(entity)
    with pytest.raises(InvalidProvClassForThisRelation):
        activity.used(activity)  # type: ignore
    with pytest.raises(InvalidProvClassForThisRelation):
        activity.used(agent)  # type: ignore


def test_acted_on_behalf_of():
    agent.acted_on_behalf_of(agent)
    with pytest.raises(InvalidProvClassForThisRelation):
        agent.acted_on_behalf_of(activity)  # type: ignore
    with pytest.raises(InvalidProvClassForThisRelation):
        agent.acted_on_behalf_of(entity)  # type: ignore


def test_started_at_time():
    activity.started_at_time(datetime(1980, 1, 1))
    with pytest.raises(NoDateTime):
        activity.started_at_time("01.01.1980")  # type: ignore
    with pytest.raises(NoDateTime):
        activity.started_at_time(1980)  # type: ignore


def test_ended_at_time():
    activity.ended_at_time(datetime(1981, 1, 1))
    with pytest.raises(NoDateTime):
        activity.ended_at_time("01.01.1981")  # type: ignore
    with pytest.raises(NoDateTime):
        activity.ended_at_time(1981)  # type: ignore