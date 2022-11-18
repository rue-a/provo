from datetime import datetime
from provo import ProvOntologyGraph

prov_ontology_graph = ProvOntologyGraph(
    namespace='http://example.org#',
    namespace_abbreviation=""
)

crime_data = prov_ontology_graph.add_entity(id_string='crimeData', label='Crime Data')
national_regions_list = prov_ontology_graph.add_entity(id_string='nationalRegionsList', label='National Regions List')
aggregated_by_regions = prov_ontology_graph.add_entity(id_string='aggregatedByRegions', label='Aggregated by Regions')
bar_chart = prov_ontology_graph.add_entity(id_string='bar_chart', label='Bar Chart')

aggregation_activity = prov_ontology_graph.add_activity(id_string='aggregationActivity', label='Aggregation Activity')
illustration_activity = prov_ontology_graph.add_activity(id_string='illustrationActivity', label='Illustration Activity')

government = prov_ontology_graph.add_agent(id_string='government', label='Government')
civil_action_group = prov_ontology_graph.add_agent(id_string='civil_action_group', label='Civil Action Group')
national_newspaper_inc = prov_ontology_graph.add_agent(id_string='national_newspaper_inc', label='National Newspaper Inc.')
derek = prov_ontology_graph.add_agent(id_string='derek', label='Derek')

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

# print(prov_ontology_graph)
prov_ontology_graph.serialize_as_rdf('provenance_graph_example.ttl')
