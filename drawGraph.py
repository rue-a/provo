import rdflib
from rdflib import Graph, Literal, BNode, URIRef, Namespace
from rdflib.namespace import DC, FOAF, RDF, RDFS
from rdflib.plugins.sparql import prepareQuery
import networkx as nx
import matplotlib.pyplot as plt

# setup namespaces
PROV = Namespace("http://www.w3.org/ns/prov#")
GEOKUR =  Namespace("https://geokur.geo.tu-dresden.de/")

def getRDFSLabel(graph, node):
    label = [k for k in graph.query(
        """SELECT ?label
        WHERE {
            ?node rdfs:label ?label .
        }
        """,
        initBindings = {'node': node}
    )][0][0]
    return label

def mapNodes(graph, nodes):
    # map labels of rdf graph as names for nodes in visualization
    # prevent duplicate names (duplicate labels in RDF are possible)
    numbers = [str(k) for k in range(10)]
    mapping = {}
    uniqueLabels = []
    for node in nodes:
        currentLabel = str(getRDFSLabel(graph, node))
        if currentLabel in uniqueLabels:
            splitLabel = currentLabel.split('-')
            if len(splitLabel) <= 1:
                currentLabel += '-2'
            else:
                if currentLabel[-1] not in numbers:
                    currentLabel += '-2'
                else:
                    currentLabel = splitLabel[0] + str(int(splitLabel[-1])+1)
        uniqueLabels.append(currentLabel)
        mapping[node] = currentLabel
    return mapping


def draw(graph, path):
    G = nx.DiGraph(directed = True)

    processPath = [k for k in graph.query(
        """SELECT ?process ?previousProcess 
        WHERE {
            ?process ^prov:wasInformedBy ?previousProcess .
            ?process a geokur:Process .
            ?previousProcess a geokur:Process . 
        }
        """, initNs = {'geokur': GEOKUR, 'prov': PROV}
    )]

    processes = [k[0] for k in graph.query(
        """SELECT ?process
        WHERE {
            ?process a geokur:Process .
        }
        """
    )]
    subProcessPaths = [k for k in graph.query(
        """SELECT ?process ?subProcess
        WHERE {
            ?process geokur:hasSubProcess ?subProcess .
            ?process a geokur:Process .
        }
        """
    )]
    subProcesses = [sub[1] for sub in subProcessPaths]

    

    # get all node, remove duplicated via set
    nodes = list(set(processes + subProcesses))
    mapping = mapNodes(graph, nodes)



    # add processes and label edges
    edgeLabels = {}
    informedEdges = []
    for pp in processPath:
        informedEdges.append((mapping.get(pp[0]), mapping.get(pp[1])))
        edgeLabels[(mapping.get(pp[0]),mapping.get(pp[1]))] = 'informed'    
    G.add_edges_from(informedEdges)


    # add subprocesses and label edges
    hasSubProcessEdges = []
    for spp in subProcessPaths:
        hasSubProcessEdges.append((mapping.get(spp[0]), mapping.get(spp[1])))
        edgeLabels[mapping.get(spp[0]), mapping.get(spp[1])] = 'hasSubProcess'
    G.add_edges_from(hasSubProcessEdges)

    


    pos = nx.spring_layout(G)
    edgeColors = ['black' if e in informedEdges else 'grey' for e in G.edges]
    edgeWidths = [1.5 if e in informedEdges else 1 for e in G.edges]
    nodeColors = ['lightblue' if n in [mapping.get(k) for k in processes] else 'lightgrey' for n in G.nodes]
    # nodeSizes = [850 if n in [mapping.get(k) for k in processes] else 500 for n in G.nodes]
    # print(nodeSizes)
    # print(transparency)

    importance = dict([(mapping.get(k[0]), float(k[1])) for k in graph.query(
        """SELECT ?node ?importance
        WHERE {
            ?node geokur:hasRelativeImportance ?importance .
        }
        """
    )])
    nodeSizes = [importance.get(n)*10000 for n in G.nodes]
    # print(nodeTransparency)
    nx.draw(G,pos,
        edge_color=edgeColors,
        width=edgeWidths,
        node_color=nodeColors,
        linewidths=1,
        node_size=nodeSizes)
    nx.draw_networkx_labels(G,pos)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edgeLabels)

    
    # edges=[['A ','B'],['B','C'],['B','D']]
    # G=nx.Graph()
    # G.add_edges_from(edges)
    # pos = nx.spring_layout(G)
    # plt.figure()    
    # nx.draw(G,pos,edge_color='black',width=1,linewidths=1,\
    # node_size=500,node_color='pink',alpha=0.9,\
    # labels={node:node for node in G.nodes()})
    # nx.draw_networkx_edge_labels(G,pos,edge_labels={('A ','B'):'AB',\
    # ('B','C'):'BC',('B','D'):'BD'},font_color='red')

    plt.savefig(path)
    print('Generated graphic at "' + path + '".')
    plt.close()

 