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
# id: str = "",
# label: str = "",
# description: str = "",
# namespace: bool = False
entity = prov_ontology_graph.add_entity(
    id="example_entity",
    label="Example Entity",
    use_namespace=True)

activity = prov_ontology_graph.add_activity(
    label="Anonymous activity",
    description="An arbitrary activity."
)

entity.was_generated_by(activity)

print(entity)

print(activity)


# ex3

prov_ontology_graph.serialize_as_rdf("examples/serialize_as_rdf.ttl")


# ex4

rdflib_graph = prov_ontology_graph.get_rdflib_graph()

rdflib_graph.bind("skos", SKOS)

rdflib_graph.add((
    URIRef(entity.node_id), SKOS.prefLabel, Literal(
        entity.label, lang="en")
))

rdflib_graph.serialize("examples/rdflib_interface.ttl")


# ex5

prov_ontology_graph.export_as_mermaid_flowchart(
    file_name="examples/manual_examples_flowchart_default.md")


# ex6

options = {
    "orientation": "LR",
    "revert-relations": True,
    "activity": {
        "fill": "#89e6dc",
        "shape": "{{:}}"
    }
}

prov_ontology_graph.export_as_mermaid_flowchart(
    file_name="examples/manual_examples_flowchart.md", user_options=options)
