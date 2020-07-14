import rdflib
from rdflib import Graph, Literal, BNode, URIRef, Namespace
from rdflib.namespace import DC, FOAF, RDF, RDFS
from rdflib.plugins.sparql import prepareQuery
import networkx as nx
import matplotlib.pyplot as plt



# setup namespaces
PROV = Namespace("http://www.w3.org/ns/prov#")
GEOKUR =  Namespace("https://geokur.geo.tu-dresden.de/namespace#")

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

def generateProcessLayout(graph, mapping, stepwideX = 1, stepwideY = 0):
    def verticalLayout (nodes, layout, currentX, currentY, verticalBuffer):
        verticalCount = len(nodes)
        if verticalCount % 2 == 0:
            start = -0.5 * verticalBuffer
        else:
            start = 0
        currentY += start
        jump = 0
        for i, process in enumerate(nodes):
            jump = i * verticalBuffer
            if i % 2 == 0:
                jump *= -1 
            currentY += jump
            layout[mapping.get(process)] = (currentX, currentY)
        return(layout)

    leftProcesses = [ k[0] for k in graph.query(
        """SELECT ?process
        WHERE {
            ?process a geokur:Process .
            FILTER( NOT EXISTS{ ?process prov:wasInformedBy ?previousProcess . } )
        }
        """, initNs = {'geokur': GEOKUR, 'prov': PROV}
    )]    

    layout = {}
    currentX = 0
    currentY = 0
    layout = verticalLayout(leftProcesses, layout, currentX, currentY, verticalBuffer = stepwideX)    
    currentX+=stepwideX
    currentY+=stepwideY
    
    
    while(True):
        rightProcesses = []
        for process in leftProcesses:
            for rightProcess in [k[0] for k in graph.triples((None, PROV.wasInformedBy, process))]:
                if rightProcess not in rightProcesses:
                    rightProcesses.append(rightProcess)
        if (len(rightProcesses) == 0):
            break
        layout = verticalLayout(rightProcesses, layout, currentX, currentY, verticalBuffer = stepwideX)   
        leftProcesses = rightProcesses
        currentX+=stepwideX
        currentY-=stepwideY
    return(layout)

def draw(graph, path):
    G = nx.DiGraph(directed = True)


    subProcessPath = [k for k in graph.query(
        """SELECT ?process ?subProcess
        WHERE {
            ?process geokur:hasSubProcess ?subProcess .
        }
        """
    )]
    processes = [k[0] for k in subProcessPath] + [k[1] for k in subProcessPath]




    

    # get all node, remove duplicated via set
    nodes = []
    nodes += list(set(processes))
    # nodes += list(set(data))
    mapping = mapNodes(graph, nodes)



    # add processes and label edges
    edgeLabels = {}
    hasSubProcessEdges = []
    if len(subProcessPath) > 0:
        for edge in subProcessPath:
            hasSubProcessEdges.append((mapping.get(edge[0]), mapping.get(edge[1])))
            edgeLabels[(mapping.get(edge[0]),mapping.get(edge[1]))] = 'hasSubProcess'    
        G.add_edges_from(hasSubProcessEdges)
    else:
        G.add_nodes_from([mapping.get(k) for k in nodes])


    edgeColors = ['black' if e in hasSubProcessEdges else 'grey' for e in G.edges]
    edgeWidths = [1.5 if e in hasSubProcessEdges else 1 for e in G.edges]
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
    print(importance)
    print(G.nodes)
    nodeSizes = [importance.get(n)*100000 for n in G.nodes]
    print(nodeSizes)
    print(hasSubProcessEdges)

    
    plt.figure(figsize=(20,4.5))
    nx.draw(G, pos=nx.planar_layout(G),
        edge_color=edgeColors,
        width=edgeWidths,
        node_color = nodeColors,
        # node_color=nodeSizes,        
        # cmap=plt.cm.Reds,
        linewidths=1,
        node_size=nodeSizes)
    nx.draw_networkx_labels(G,pos=nx.planar_layout(G))
    # print(edgeLabels)
    nx.draw_networkx_edge_labels(G,pos=nx.planar_layout(G),edge_labels=edgeLabels)

    
    plt.savefig(path, bbox_inches='tight', pad_inches = 0)
    print('Generated graphic at "' + path + '".')
    plt.close()


g = rdflib.Graph()
g.parse('./out/exGernal-3.rdf', format='n3')
draw(g, './graphics/test.png')