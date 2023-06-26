
import pprint
from datetime import datetime
from rdflib import FOAF, RDF, Literal, URIRef  # type: ignore

import rdflib
from pathlib import Path
from provo.provontologygraph import ProvOntologyGraph

THIS_DIR = Path(__file__).resolve().parent


def test_graph_isomorphism_short_ex():
    graph = ProvOntologyGraph()

    poster = graph.add_entity(
        "https://doi.org/10.6084/m9.figshare.23561661", label="this graphic"
    )
    script = graph.add_activity(
        "https://github.com/rue-a/provo-poster", "provo script")
    me = graph.add_agent("https://orcid.org/0000-0001-8637-9071", "author")
    slub = graph.add_agent("https://ror.org/03wf51b65", "SLUB")

    poster.was_generated_by(script)
    poster.was_attributed_to(me)
    script.was_associated_with(me)
    me.acted_on_behalf_of(slub)

    target_graph = rdflib.Graph()
    target_graph.parse(THIS_DIR / "rdf_output_short_ex.ttl")
    # Assert that the sets of triples are equal
    assert set(graph.get_rdflib_graph()) == set(target_graph)


def test_graph_isomorphism_long_ex():

    prov_ontology_graph = ProvOntologyGraph(
        namespace='http://example.org#',
        namespace_abbreviation=""
    )

    # create entities
    crime_data = prov_ontology_graph.add_entity(
        id='crimeData', label='Crime Data', use_namespace=True)
    national_regions_list = prov_ontology_graph.add_entity(
        id='nationalRegionsList', label='National Regions List', use_namespace=True)
    aggregated_by_regions = prov_ontology_graph.add_entity(
        id='aggregatedByRegions', label='Aggregated by Regions', use_namespace=True)
    bar_chart = prov_ontology_graph.add_entity(
        id='bar_chart', label='Bar Chart', use_namespace=True)

    # create activities
    aggregation_activity = prov_ontology_graph.add_activity(
        id='aggregationActivity', label='Aggregation Activity', use_namespace=True)
    illustration_activity = prov_ontology_graph.add_activity(
        id='illustrationActivity', label='Illustration Activity', use_namespace=True)

    # create agents
    government = prov_ontology_graph.add_agent(
        id='government', label='Government', use_namespace=True)
    civil_action_group = prov_ontology_graph.add_agent(
        id='civil_action_group', label='Civil Action Group', use_namespace=True)
    national_newspaper_inc = prov_ontology_graph.add_agent(
        id='national_newspaper_inc', label='National Newspaper Inc.', use_namespace=True)
    derek = prov_ontology_graph.add_agent(
        id='derek', label='Derek', use_namespace=True)

    # build relations
    crime_data.was_attributed_to(government)
    national_regions_list.was_attributed_to(civil_action_group)

    aggregation_activity.used(crime_data)
    aggregation_activity.used(national_regions_list)
    aggregation_activity.started_at_time(datetime(2011, 7, 14, 1, 1, 1))
    aggregation_activity.ended_at_time(datetime(2011, 7, 14, 2, 2, 2))
    aggregation_activity.was_associated_with(derek)

    aggregated_by_regions.was_generated_by(aggregation_activity)
    aggregated_by_regions.was_attributed_to(derek)

    illustration_activity.was_informed_by(aggregation_activity)
    illustration_activity.used(aggregated_by_regions)
    illustration_activity.was_associated_with(derek)

    bar_chart.was_generated_by(illustration_activity)
    bar_chart.was_derived_from(aggregated_by_regions)
    bar_chart.was_attributed_to(derek)

    derek.acted_on_behalf_of(national_newspaper_inc)

    # print graph to terminal
    print(prov_ontology_graph)

    # use rdflib interface to add FOAF triples
    rdflib_graph = prov_ontology_graph.get_rdflib_graph()

    rdflib_graph.bind("foaf", FOAF)

    rdflib_graph.add((
        URIRef(government.node_id),
        RDF.type,
        FOAF.Organization
    ))

    rdflib_graph.add((
        URIRef(civil_action_group.node_id),
        RDF.type,
        FOAF.Organization
    ))

    rdflib_graph.add((
        URIRef(national_newspaper_inc.node_id),
        RDF.type,
        FOAF.Organization
    ))

    rdflib_graph.add((
        URIRef(national_newspaper_inc.node_id),
        FOAF.name,
        Literal(national_newspaper_inc.label, lang="en")
    ))

    rdflib_graph.add((
        URIRef(derek.node_id),
        RDF.type,
        FOAF.Person
    ))

    rdflib_graph.add((
        URIRef(derek.node_id),
        FOAF.givenName,
        Literal(derek.label, lang="en")
    ))

    rdflib_graph.add((
        URIRef(derek.node_id),
        FOAF.mbox,
        URIRef("mailto:derek@example.org")
    ))

    target_graph = rdflib.Graph()
    target_graph.parse(THIS_DIR / "rdf_output_long_ex.ttl")
    rdflib_graph.serialize(THIS_DIR / 'test.ttl')

    # Assert that the sets of triples are equal
    assert set(rdflib_graph) == set(target_graph)
