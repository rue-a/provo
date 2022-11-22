# README

The package supports the creation of [PROV-O](https://www.w3.org/TR/prov-o/) compliant provenance graphs. 

The package requires __Python 3.11__.

## Installation

You can install the package from the Python Package Index (PyPI):

`pip install provo`

Or by downloading this repo:

1. Download and unzip the package
2. Open Shell and _cd_ to unzipped package
3. Run `pip install -e .` (in the folder that contains ```setup.py```)


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

- The package implements full type hint support, thus enabling rich support from the IDE.
- The classes `Provence_Ontology_Graph`, `Entity`, `Activity`, and `Agent` can be printed to terminal in a user-friendly, readable way with the default `print()` command.
- for some quick testing, objects of the classes `Entity`, `Activity`, and `Agent` can be instantiated with auto-generated Ids (although it's not recommended using this for production).

### Interface to RDF via the [rdflib](https://rdflib.readthedocs.io/en/stable/) package

- The graph's contents can be converted to an `rdflib.Graph` object.
- The graph can be exported in various RDF serializations.

## Manual

The package is centered around the class ProvenanceOntologyGraph. Entities, Activities, and Agents are added to this graph by using the according add-methods. Relations between the starting point classes are constructed by using the respective methods of the classes. 


### Create a Provenance Ontology Graph

The graph can be initialized with default or user defined attributes. The graph can be printed to the terminal with `print(graph)`.

```python
# ex1 - create a provenance graph
from provo import ProvOntologyGraph

# __defaults__
# namespace: str = "https://provo-example.org/",
# namespace_abbreviation: str = "", 
# lang: str = "en"
provenance_graph = ProvOntologyGraph()

prov_ontology_graph = ProvOntologyGraph(
    namespace='http://example.org#',
    namespace_abbreviation="ex",
    lang="en"
)
```

`namespace=`

- Default is `"https://provo-example.org/"`.
- Has to be valid url, validation is currently performed with the [validators]() package.
- Has to end with `/` or `#`.

`namespace_abbreviation=`

- Default is `""`.
- Used when converting to other models, such as RDF (-> prefixes)
- Only characters from the Latin alphabet are allowed.
- RDF core prefixes (*owl*, *rdf*, *rdfs*, *xsd* and *xml*) are prohibited from use.

>**Note** 
> Although not prohibited, the following prefixes are commonly uses and thus recommended to be avoided: *brick*, *csvw*, *dc*, *dcat*, *dcmitype*, *cdterms*, *dcam*, *doap*, *foaf*, *geo*, *odrl*, *org*, *prof*, *prov*, *qb*, *sdo*, *sh*, *skos*, *sosa*, *ssn*, *time*, *vann* and *void*.

`lang=`

- Default is `"en"`.
- Used when converting to other models that support a *lang* tag.
- Has to be compliant with [RFC 5646](https://www.rfc-editor.org/info/rfc5646) (Phillips, A., Ed., and M. Davis, Ed., "Tags for Identifying Languages", BCP 47, RFC 5646, September 2009). Compliance is not validated!

### Create Entities, Activities and Agents and define relation between them

The creation for the three starting term classes follows the same pattern. The classes only differ in their methods. PROV-O Classes are instantiated by using the add methods of the provenance graph class. Below you find an extensively commented version of the `add_entity()` method. 

```python
def add_entity(self, id_string: str = "", label: str = "", description: str = "", namespace: str = "") -> Entity:
    """creates a new entity, adds it to the graph and returns it then"""

    # the id of the PROV class objects is a combination of the 
    # namespace and the id_string. The method _handle_id() builds 
    # the actual id of the node, if checks whether the provided 
    # namespace-id combination is already used for a node in the graph.
    # if no namespace is provided: default namespace is used, 
    # if no id is provided: id get automatically generated.
    node_id = self._handle_id(namespace, id_string)
    # the PROV class (in this case an Entity) is only created if everything with the ID is fine
    entity = Entity(
        # mandatory
        node_id=node_id,
        # optional
        label=label,
        # optional
        description=description)
    self._entities.append(entity)
    return entity
```

The relations are defined by calling the respective methods of the PROV class instances.

Example use of the provenance graph's add-methods and the definition of a *used*-relation between an Activity and an Entity:

```python
# ex2 - create entities, activities and agents, 
# and define relation between them
entity = prov_ontology_graph.add_entity(
    id_string="example_entity",
    label="Example Entity")

activity = prov_ontology_graph.add_activity(
    label="Anonymous activity",
    description="An arbitrary activity."
)

activity.used(entity)

print(entity)
# id: http://example.org#example_entity
# label: Example Entity
# ---

print(activity)
# id: http://example.org#94021a6a-40cd-4c02-9571-33480488ff82
# label: Anonymous activity
# description: An arbitrary activity.
# used: ['Example Entity']
# ---
```

### RDF interface

The graph can be directly serialized as RDF document or be converted to an rdflib Graph, for further manipulation.

```python
# ex3 - serialize provenance graph as RDF document
prov_ontology_graph.serialize_as_rdf("manual_examples.ttl")
```

```
@prefix : <http://example.org#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

:94021a6a-40cd-4c02-9571-33480488ff82 a prov:Activity ;
    rdfs:label "Anonymous activity"@en ;
    rdfs:comment "An arbitrary activity."@en ;
    prov:used :example_entity .

:example_entity a prov:Entity ;
    rdfs:label "Example Entity"@en .
```

```python
# ex4 - interface with rdflib

from rdflib import SKOS, Literal, URIRef

rdflib_graph = prov_ontology_graph.get_rdflib_graph()

rdflib_graph.bind("skos", SKOS)

rdflib_graph.add((
    URIRef(entity.get_id()), 
    SKOS.prefLabel, 
    Literal(entity.get_label(), lang="en")
))

rdflib_graph.serialize("examples/rdflib_interface.ttl")
```
```
@prefix : <http://example.org#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .

:94021a6a-40cd-4c02-9571-33480488ff82 a prov:Activity ;
    rdfs:label "Anonymous activity"@en ;
    rdfs:comment "An arbitrary activity."@en ;
    prov:used :example_entity .

:example_entity a prov:Entity ;
    rdfs:label "Example Entity"@en ;
    skos:prefLabel "Example Entity"@en .
```




## Comprehensive Examples

Code to create the PROV-O [example 1](https://www.w3.org/TR/prov-o/#narrative-example-simple-1)

```python
from datetime import datetime

from provo import ProvOntologyGraph
from rdflib import FOAF, RDF, Literal, URIRef

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
```


## Used Packages

- rdflib: https://rdflib.readthedocs.io/en/stable/, BSD License
- validators: https://github.com/python-validators/validators, MIT License


## License

GNU General Public License v3.0

## Contact

Arne Rümmler ([arne.ruemmler@gmail.com](mailto:arne.ruemmler@gmail.com))
