from datetime import datetime

from provo import ProvOntologyGraph
from rdflib import FOAF, RDF, Literal, URIRef  # type: ignore

# create example from: https://www.w3.org/TR/prov-o/#narrative-example-simple-1


# create graph
prov_ontology_graph = ProvOntologyGraph(
    namespace='http://example.org#',
    namespace_abbreviation=""
)

# create entities
crime_data = prov_ontology_graph.add_entity(id_string='crimeData', label='Crime Data')
national_regions_list = prov_ontology_graph.add_entity(id_string='nationalRegionsList', label='National Regions List')
aggregated_by_regions = prov_ontology_graph.add_entity(id_string='aggregatedByRegions', label='Aggregated by Regions')
bar_chart = prov_ontology_graph.add_entity(id_string='bar_chart', label='Bar Chart')

# create activities
aggregation_activity = prov_ontology_graph.add_activity(id_string='aggregationActivity', label='Aggregation Activity')
illustration_activity = prov_ontology_graph.add_activity(id_string='illustrationActivity', label='Illustration Activity')

# create agents
government = prov_ontology_graph.add_agent(id_string='government', label='Government')
civil_action_group = prov_ontology_graph.add_agent(id_string='civil_action_group', label='Civil Action Group')
national_newspaper_inc = prov_ontology_graph.add_agent(id_string='national_newspaper_inc', label='National Newspaper Inc.')
derek = prov_ontology_graph.add_agent(id_string='derek', label='Derek')

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
