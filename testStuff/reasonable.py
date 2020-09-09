# %%
import rdflib
import reasonable

g = rdflib.Graph()
g.parse('ex.ttl', format = 'turtle')

r = reasonable.PyReasoner()
r.from_graph(g)
triples = r.reason()
print(triples)