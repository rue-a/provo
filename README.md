# README

The package supports the creation of [PROV-O](https://www.w3.org/TR/prov-o/) compliant provenance graphs. 

The package requires __Python 3.11__.

## Installation

`pip install provo`

## Contents

The package implements the [PROV-O starting point classes](https://www.w3.org/TR/prov-o/#starting-points-figure) __Entity__, __Activity__ and __Agent__ as Python classes with methods to establish starting point properties between them instances of these classes. 

## Features

### Compliance

- The PROV-O classes __Entity__, __Activity__, and __Agent__ are implemented as Python classes.
- The PROV-O properties _wasGeneratedBy_, _wasDerivedFrom_, _wasAttributedTo_, _startedAtTime_, _used_, _wasInformedBy_, _endedAtTime_, _wasAssociatedWith_, and _actedOnBehalfOf_ are implemented as instance methods of their according classes.
- Attributes that are passes to these methods are type-checked to enforce compliance with PROV-O.
itemName=ms-python.vscode-pylance).
- Node Ids are checked for validity.
- Accidental use of the same ID for different objects throws an error.

### Ease of Use

- The package implements full type hint support, thus enabling rich support from linters such as [Pylance](https://marketplace.visualstudio.com/items).
- The classes `Provence_Ontology_Graph`, `Entity`, `Activity`, and `Agent` can be printed to terminal in a user-friendly, readable way with the default `print()` command.

- for some quick testing, objects of the classes `Entity`, `Activity`, and `Agent` can be instantiated with auto-generated Ids (although it's not recommended using this for production).

### Interface to RDF via the [rdflib](https://rdflib.readthedocs.io/en/stable/) package

- The graph's contents can be converted to an `rdflib.Graph` object.
- The graph can be exported in various RDF serializations.

## Examples

Code to create the PROV-O [example 1](https://www.w3.org/TR/prov-o/#narrative-example-simple-1)

```python
from datetime import datetime
from provo import ProvOntologyGraph

# create graph
prov_ontology_graph = ProvOntologyGraph(
    namespace='http://example.org#',
    namespace_abbreviation=""
)

# create entities
crime_data = prov_ontology_graph.add_entity(
    id_string='crimeData', label='Crime Data')
national_regions_list = prov_ontology_graph.add_entity(
    id_string='nationalRegionsList', label='National Regions List')
aggregated_by_regions = prov_ontology_graph.add_entity(
    id_string='aggregatedByRegions', label='Aggregated by Regions')
bar_chart = prov_ontology_graph.add_entity(
    id_string='bar_chart', label='Bar Chart')

# create activities
aggregation_activity = prov_ontology_graph.add_activity(
    id_string='aggregationActivity', label='Aggregation Activity')
illustration_activity = prov_ontology_graph.add_activity(
    id_string='illustrationActivity', label='Illustration Activity')

# create agents
government = prov_ontology_graph.add_agent(
    id_string='government', label='Government')
civil_action_group = prov_ontology_graph.add_agent(
    id_string='civil_action_group', label='Civil Action Group')
national_newspaper_inc = prov_ontology_graph.add_agent(
    id_string='national_newspaper_inc', label='National Newspaper Inc.')
derek = prov_ontology_graph.add_agent(
    id_string='derek', label='Derek')

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

# serialize graph as rdf document
prov_ontology_graph.serialize_as_rdf('provenance_graph_example.ttl')

```


## Used Packages

- rdflib: https://rdflib.readthedocs.io/en/stable/, BSD License
- validators: https://github.com/python-validators/validators, MIT License


## License

GNU General Public License v3.0

## Contact

Arne Rümmler ([arne.ruemmler@gmail.com](mailto:arne.ruemmler@gmail.com))
