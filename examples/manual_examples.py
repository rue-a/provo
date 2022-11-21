from provo import ProvOntologyGraph
from rdflib import SKOS, Literal, URIRef

# ex1
# __defaults__
# namespace: str = "https://provo-example.org/",
# namespace_abbreviation: str = "",
# lang: str = "en"
provenance_graph = ProvOntologyGraph()

prov_ontology_graph = ProvOntologyGraph(
    namespace='http://example.org#',
    namespace_abbreviation="",
    lang="en"
)

# ex2
# __defaults__
# id_string: str = "",
# label: str = "",
# description: str = "",
# namespace: str = ""
entity = prov_ontology_graph.add_entity(
    id_string="example_entity",
    label="Example Entity")

activity = prov_ontology_graph.add_activity(
    label="Anonymous activity",
    description="An arbitrary activity."
)

activity.used(entity)

print(entity)

print(activity)


# ex3

prov_ontology_graph.serialize_as_rdf("examples/serialize_as_rdf.ttl")


# ex4

rdflib_graph = prov_ontology_graph.get_rdflib_graph()

rdflib_graph.bind("skos", SKOS)

rdflib_graph.add((
    URIRef(entity.get_id()), SKOS.prefLabel, Literal(entity.get_label(), lang="en")
))

rdflib_graph.serialize("examples/rdflib_interface.ttl")
