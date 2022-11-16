from provo import ProvOntologyGraph

prov_ontology_graph = ProvOntologyGraph(namespace="https://prov-test.org/")


entity = prov_ontology_graph.new_entity(id="new_id")
entity2 = prov_ontology_graph.new_entity()

print(prov_ontology_graph)
