# %%
import ProvGraph
from rdflib import Literal, BNode, URIRef, Namespace
from rdflib.namespace import DC, FOAF, RDF, RDFS
# setup custom namespaces
PROV = Namespace("http://www.w3.org/ns/prov#")
GEOKUR =  Namespace("https://geokur.geo.tu-dresden.de/")
EX = Namespace("https://example.com/")

g = ProvGraph.ProvGraph()

# 
g.parse("test.rdf", format = 'n3')
g.serializeGranularities('./granularities/test')

print('finished')

# # %%
# import ProvGraph
# from rdflib import Graph
# from rdflib import URIRef
# from rdflib.plugins.sparql import prepareQuery



# LOGs =  list(range(0,10))
# for LOG in LOGs:
#     graph = Graph()
#     inName = "./granularities/test_LOG"+ str(LOG) +".rdf"
#     graph.parse(inName, format = 'n3')
#     processThread = prepareQuery(
#         """
#         SELECT
#         ?process ?rel ?sourceProcess
#         WHERE
#         {
#             ?process ?rel ?sourceProcess .
#             FILTER (
#                 ?rel IN (prov:wasInformedBy)
#             )
#         }
#         """,
#         initNs = { 
#             "prov": PROV, 
#             "geokur": GEOKUR
#         }
#     )
#     dataThread = prepareQuery(
#         """
#         SELECT
#         ?process ?rel ?sourceProcess
#         WHERE
#         {
#             ?process ?rel ?sourceProcess .
#             FILTER (
#                 ?rel IN (prov:wasDerivedFrom)
#             )
#         }
#         """,
#         initNs = { 
#             "prov": PROV, 
#             "geokur": GEOKUR
#         }
#     )
#     processAndDataThread = prepareQuery(
#         """
#         SELECT
#         ?process ?rel ?sourceProcess
#         WHERE
#         {
#             ?process ?rel ?sourceProcess .
#             FILTER (
#                 ?rel IN (prov:used, prov:wasGeneratedBy,prov:wasInformedBy, prov:wasDerivedFrom)
#             )
#         }
#         """,
#         initNs = { 
#             "prov": PROV, 
#             "geokur": GEOKUR
#         }
#     )

#     visGraph = ProvGraph.ProvGraph()
#     for row in graph.query(processThread):
#         s = row[0]
#         p = row[1]
#         o = row[2]
#         visGraph.add((s,p,o))
#     name = './granularities/processThread_LOG' + str(LOG) + '.rdf'
#     visGraph.serialize(format = 'n3', destination = name)

#     visGraph = ProvGraph.ProvGraph()
#     for row in graph.query(dataThread):
#         s = row[0]
#         p = row[1]
#         o = row[2]
#         visGraph.add((s,p,o))
#     name = './granularities/dataThread_LOG' + str(LOG) + '.rdf'
#     visGraph.serialize(format = 'n3', destination = name)

#     visGraph = ProvGraph.ProvGraph()
#     for row in graph.query(processAndDataThread):
#         s = row[0]
#         p = row[1]
#         o = row[2]
#         visGraph.add((s,p,o))
#         name = './granularities/processAndDataThread_LOG' + str(LOG) + '.rdf'
#     visGraph.serialize(format = 'n3', destination = name)


print('finished')









# from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph
# import networkx as nx
# import matplotlib.pyplot as plt


# G = rdflib_to_networkx_multidigraph(processGraph)

# # Plot Networkx instance of RDF Graph
# pos = nx.spring_layout(G, scale=2)
# edge_labels = nx.get_edge_attributes(G, 'r')
# nx.draw_networkx_edge_labels(G, pos, labels=edge_labels)
# nx.draw(G, with_labels=True)
# plt.show()







# %%
