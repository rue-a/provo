from datetime import datetime

from rdflib import FOAF, RDF, Literal, URIRef  # type: ignore

from provo import ProvOntologyGraph

# create example from: https://www.w3.org/TR/prov-o/#narrative-example-simple-1


# create graph
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
derek = prov_ontology_graph.add_agent(id='derek', label='Derek')

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
    URIRef(government.get_id()),
    RDF.type,
    FOAF.Organization
))

rdflib_graph.add((
    URIRef(civil_action_group.get_id()),
    RDF.type,
    FOAF.Organization
))

rdflib_graph.add((
    URIRef(national_newspaper_inc.get_id()),
    RDF.type,
    FOAF.Organization
))

rdflib_graph.add((
    URIRef(national_newspaper_inc.get_id()),
    FOAF.name,
    Literal(national_newspaper_inc.get_label(), lang="en")
))

rdflib_graph.add((
    URIRef(derek.get_id()),
    RDF.type,
    FOAF.Person
))

rdflib_graph.add((
    URIRef(derek.get_id()),
    FOAF.givenName,
    Literal(derek.get_label(), lang="en")
))

rdflib_graph.add((
    URIRef(derek.get_id()),
    FOAF.mbox,
    URIRef("mailto:derek@example.org")
))
# serialize graph as rdf document
rdflib_graph.serialize('examples/provenance_graph_example.ttl')

# export as mermaid flowchart
options = {
    "revert-relations": True,
    "entity": {
        "shape": "[:]",
        "fill": "#FC766AFF",
        "stroke": "#FC766AFF",
        "color": "333"
    },
    "agent": {
        "shape": "[/:\\]",
        "stroke": "#B0B8B4FF",
        "fill": "#B0B8B4FF",
        "color": "333",
        "relation-style": "."
    },
    "activity": {
        "shape": "{{:}}",
        "fill": "#184A45FF",
        "stroke": "#184A45FF",
        "color": "#eee"
    }
}

# with adjusted options
prov_ontology_graph.export_as_mermaid_flowchart(
    file_name="examples/provenance_mermaid.md",
    user_options=options)

# with default_options
prov_ontology_graph.export_as_mermaid_flowchart(
    file_name="examples/provenance_mermaid_default.md")
