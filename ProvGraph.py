from rdflib import Graph, Literal, BNode, URIRef, Namespace
from rdflib.namespace import DC, FOAF, RDF, RDFS
from rdflib.plugins.sparql import prepareQuery
import pandas as pd
import csv

import drawGraph
# setup namespaces
PROV = Namespace("http://www.w3.org/ns/prov#")
GEOKUR =  Namespace("https://geokur.geo.tu-dresden.de/")
ARCGIS = Namespace("https://pro.arcgis.com/de/pro-app/tool-reference/")

class ProvGraph(Graph):
    mergeCount = 1
    CNS = Namespace("https://customNamespace.com/")
    with open('tags.csv') as f:
        _tags = dict(filter(None, csv.reader(f)))
    with open('tagMetrics.csv') as f:
        _tagMetrics = dict(filter(None, csv.reader(f)))
    def __init__(self, store='default', namespace = None, identifier=None, namespace_manager=None):
        super().__init__(store=store, identifier=identifier, namespace_manager=namespace_manager)
        if namespace:
            self.CNS = Namespace(namespace)
        self.add((GEOKUR.Process, RDFS.subClassOf, PROV.Activity))
        self.add((GEOKUR.SubProcess, RDFS.subClassOf, PROV.Activity))
        self.add((GEOKUR.Data, RDFS.subClassOf, PROV.Entity))
        self.add((GEOKUR.hasTag, RDF.type, RDF.Property))
        self.add((GEOKUR.hasRelativeImportance, RDF.type, RDF.Property))
        self.add((GEOKUR.hasSubProcess, RDF.type, RDF.Property))
        self.add((GEOKUR.isInstanceOf, RDF.type, RDF.Property))
        self.bind("dc", DC)
        self.bind("foaf", FOAF)
        self.bind("rdf", RDF)
        self.bind("rdfs", RDFS)
        self.bind("geokur", GEOKUR)
        self.bind("prov", PROV)
        self.bind("cns", self.CNS)
        self.bind("arcgis/tool-reference", ARCGIS)
    # methods for construction of the prov graph
    def addProcess(self, label, instanceOf = None):
        ID = eval('self.CNS.' + BNode())
        self.add((ID, RDF.type, GEOKUR.Process))
        self.add((ID, RDFS.label, Literal(label)))
        if (instanceOf):
            self.add((ID, GEOKUR.isInstanceOf, URIRef(instanceOf)))
        return ID
    def addData(self, label):
        ID = eval('self.CNS.' + BNode())
        self.add((ID, RDF.type, GEOKUR.Data))
        self.add((ID, RDFS.label, Literal(label)))
        return ID
    def addAgent(self, label):
        ID = eval('self.CNS.' + BNode())
        self.add((ID, RDF.type, GEOKUR.Agent))
        self.add((ID, RDFS.label, Literal(label)))
        return ID
    def link(self, inputs = None, process = None, outputs = None, agents = None):
        if inputs:
            if not isinstance(inputs, list):
                inputs = [inputs]
        if outputs:
            if not isinstance(outputs, list):
                outputs = [outputs]
        if agents:
            if not isinstance(agents,list):
                agents = [agents]        
        if (inputs and process):
            for entity in inputs:
                self.add((process, PROV.used, entity))
        if (outputs and process):
            for entity in outputs:
                self.add((entity, PROV.wasGeneratedBy, process))
        if (inputs and outputs):
            for inp in inputs:
                for out in outputs:
                    self.add((out, PROV.wasDerivedFrom, inp))
        if (agents and inputs): 
            for agent in agents:
                for inp in inputs:
                    self.add((inp, PROV.wasAttributedTo, agent))
        if (agents and outputs):
            for agent in agents:
                for output in outputs:
                    self.add((output, PROV.wasAttributedTo, agent))
        if (agents and process):
            for agent in agents:
                self.add((process, PROV.wasAssociatedWith, agent))
    
    def tagProcess(self, ID, tags):
        if not isinstance(tags, list):
            tags = [tags]
        for tag in tags:
            if tag in self._tags.keys():
                self.add((ID, GEOKUR.hasTag, Literal(tag)))
            else:
                print(' "' + tag + '" is no valid tag')

    def infereWasInformedByLinks(self):
        qRes = self.query(
            """SELECT ?p ?pp
            WHERE {
                ?p prov:used ?data .
                ?data prov:wasGeneratedBy ?pp .
            }"""
        )
        for row in qRes:
            self.add((row[0], PROV.wasInformedBy, row[1]))

    def addIOTags(self):
        processesQ = prepareQuery(
            """ SELECT ?node
            WHERE {
                ?node a geokur:Process .
            } """,
            initNs = {'geokur': GEOKUR}
        )
        inputsQ = prepareQuery(
            """ SELECT ?node
            WHERE {
                ?process prov:used ?node . 
            } """,
            initNs = {'prov': PROV}
        )
        inProcsQ = prepareQuery(
            """ SELECT ?node
            WHERE {
                ?process prov:wasInformedBy ?node . 
            } """,
            initNs = {'prov': PROV}
        )
        outputsQ = prepareQuery(
            """ SELECT ?node
            WHERE {
                ?node prov:wasGeneratedBy ?process . 
            } """,
            initNs = {'prov': PROV}
        )
        outProcsQ = prepareQuery(
            """ SELECT ?node
            WHERE {
                ?node prov:wasInformedBy ?process . 
            } """,
            initNs = {'prov': PROV}
        )
        for process in self.query(processesQ):
            process = process[0]
            # get input data
            inputs = self.query(inputsQ, initBindings = {'process': process})
            if len(inputs) > 1:
                self.add((process, GEOKUR.hasTag, Literal('multipleIns')))
            # get ingoing processes
            inProcs = self.query(inProcsQ, initBindings = {'process': process})
            if len(inProcs) > 1:
                self.add((process, GEOKUR.hasTag, Literal('root')))
            # get output data
            outputs = self.query(outputsQ, initBindings = {'process': process})
            if len(outputs) > 1:
                self.add((process, GEOKUR.hasTag, Literal('multipleOuts')))
            # get outgoing processes
            outProcs = self.query(outProcsQ, initBindings = {'process': process})
            if len(outProcs) > 1:
                self.add((process, GEOKUR.hasTag, Literal('branch')))

    def calcRelativeImportance(self):        
        processesQ = prepareQuery(
            """ SELECT ?node
            WHERE {
                ?node a geokur:Process .
            } """,
            initNs = {'geokur': GEOKUR}
        )
        tagsQ = prepareQuery(
            """SELECT ?node
            WHERE {
                ?process geokur:hasTag ?node .
            } """,
            initNs = {'geokur': GEOKUR}
        )
        importance = {}
        totalImportance = 0
        for process in self.query(processesQ):
            process = process[0]
            tags = self.query(tagsQ, initBindings = {'process': process})
            # calc absolute importance
            importance[process] = sum([int(elem) for elem in [ (self._tagMetrics[self._tags[str(tag[0])]]) for tag in tags ]])
            totalImportance += importance[process]
        for process in importance:
            importance[process] /= totalImportance
            self.add((process, GEOKUR.hasRelativeImportance, Literal(float(importance[process]))))
    
    def getMergePair(self):
        importanceQ = prepareQuery(
            """ SELECT ?process ?importance
            WHERE {
                ?process a geokur:Process .
                ?process geokur:hasRelativeImportance ?importance .

            } """,
            initNs = {'geokur': GEOKUR}
        )
        neighborQ = prepareQuery(
            """SELECT ?neighbor ?importance
            WHERE {
                {
                    ?neighbor prov:wasInformedBy ?process .
                    ?neighbor geokur:hasRelativeImportance ?importance .
                }
                UNION
                {
                    ?process prov:wasInformedBy ?neighbor . 
                    ?neighbor geokur:hasRelativeImportance ?importance .
                }

            }
            """,
            initNs = {'prov': PROV, 'geokur': GEOKUR, 'rdfs': RDFS}
        )

        # store processes with rel importance in dict
        processes = {}
        for i, result in enumerate(self.query(importanceQ)):
            processes[str(result[0])] = float(result[1])
        
        # get min importance candidates
        minval = min(processes.values())
        candidates = [k for k, v in processes.items() if v==minval]
        # get min importance neighbors with according candidate
        candidateNeighborImportance = []
        # print(candidates)
        for candidate in candidates:
            for i, result in enumerate(self.query(neighborQ, initBindings = {'process': URIRef(candidate)})):
                candidateNeighborImportance.append([str(candidate), str(result[0]), float(result[1])])
        # print(candidateNeighborImportance)
        minValNeighbors = min([val[2] for val in candidateNeighborImportance])
        # if there are multiple (candidate, neighbors) pairs with identical 
        # relative importance values, choose the first pair from the list
        # (order of the list is random // controlled by SPARQL processor)
        index = None
        for i, item in enumerate(candidateNeighborImportance):
            if item[2] == minValNeighbors:
                index = i
                # stop at first match
                break
        mergePair = candidateNeighborImportance[index]
        return (URIRef(mergePair[0]), URIRef(mergePair[1]))
    
    def merge(self, process, neighbor):
        # gather all in- and outgoing data that is not intermediate
        # gather all in- and outgoing processes
        inputDataQ = prepareQuery(
            """ SELECT ?data ?label
            WHERE {                    
                { ?leftProc prov:used ?data . }
                UNION
                { ?rightProc prov:used ?data . }
                ?data rdfs:label ?label .
            }
            """ ,
            initNs = {'prov': PROV, 'geokur': GEOKUR, 'rdfs': RDFS}
        )
        outputDataQ = prepareQuery(
            """ SELECT ?data ?label
            WHERE {                    
                ?data prov:wasGeneratedBy ?rightProc .
                ?data rdfs:label ?label .
            }
            """ ,
            initNs = {'prov': PROV, 'geokur': GEOKUR, 'rdfs': RDFS}
        )
        ingoingProcessesQ = prepareQuery(
            """ SELECT ?process ?label
            WHERE {                    
                { 
                    ?rightProc prov:wasInformedBy ?process . 
                }
                UNION
                { ?leftProc prov:wasInformedBy ?process . }
                ?process rdfs:label ?label .
            }
            """,
            initNs = {'prov': PROV, 'geokur': GEOKUR, 'rdfs': RDFS}
        )
        outgoingProcessesQ = prepareQuery(
            """SELECT ?process ?label
            WHERE {
                ?process prov:wasInformedBy ?rightProc .
                ?process rdfs:label ?label .
            }
            """,
            initNs = {'prov': PROV, 'geokur': GEOKUR, 'rdfs': RDFS}
        )
        intermediateDataQ = prepareQuery(
            """SELECT ?data ?label
            WHERE {
                ?data prov:wasGeneratedBy ?leftProc .
                ?rightProc prov:used ?data . 
                ?data rdfs:label ?label .
            }
            """,
            initNs = {'prov': PROV, 'geokur': GEOKUR, 'rdfs': RDFS}
        )
        processInfoQ = prepareQuery(
            """SELECT ?process ?label ?importance
            WHERE {
                ?process rdfs:label ?label .
                ?process geokur:hasRelativeImportance ?importance .
            }
            """,
            initNs = {'prov': PROV, 'geokur': GEOKUR, 'rdfs': RDFS}
        )
        agentQ = prepareQuery(
            """SELECT DISTINCT ?agent ?label
            WHERE {
                { ?process prov:wasAssociatedWith ?agent . }
                UNION
                { ?neighbor prov:wasAssociatedWith ?agent . }
                ?agent rdfs:label ?label .
            }
            """,
            initNs = {'prov': PROV, 'geokur': GEOKUR, 'rdfs': RDFS}
        )

        inputData = None
        outputData = None
        intermediateData = None
        ingoingProcesses = None
        outgoingProcesses = None
        if (process, PROV.wasInformedBy, neighbor) in self:
            inputData = [k for k in self.query(inputDataQ, initBindings={'leftProc': neighbor, 'rightProc': process}) if k[0] != neighbor]
            outputData = [k for k in self.query(outputDataQ, initBindings={'leftProc': neighbor, 'rightProc': process})]
            intermediateData = [ k for k in self.query(intermediateDataQ, initBindings={'leftProc': neighbor, 'rightProc': process})]
            ingoingProcesses = [k for k in self.query(ingoingProcessesQ, initBindings={'leftProc': neighbor, 'rightProc': process}) if k[0] != neighbor]
            outgoingProcesses = [k for k in self.query(outgoingProcessesQ, initBindings={'leftProc': neighbor, 'rightProc': process})]

        elif (neighbor, PROV.wasInformedBy, process) in self:
            inputData = [k for k in self.query(inputDataQ, initBindings={'leftProc': process, 'rightProc': neighbor}) if k[0] != process]
            outputData = [k for k in self.query(outputDataQ, initBindings={'leftProc': process, 'rightProc': neighbor})]
            intermediateData = [k for k in self.query(intermediateDataQ, initBindings={'leftProc': process, 'rightProc': neighbor})]
            ingoingProcesses = [k for k in self.query(ingoingProcessesQ, initBindings={'leftProc': process, 'rightProc': neighbor}) if k[0] != process]            
            outgoingProcesses = [k for k in self.query(outgoingProcessesQ, initBindings={'leftProc': process, 'rightProc': neighbor})]
        associatedAgents = [k for k in self.query(agentQ, initBindings={'neighbor': neighbor, 'process': process})]
        
        
        # get process' and neighbor's label and importance
        process = [k for k in self.query(processInfoQ, initBindings={'process': process})][0]
        neighbor = [k for k in self.query(processInfoQ, initBindings={'process': neighbor})][0]
        # print(self.mergeCount)
        
        # cut links to other process and agents
        self.remove((process[0], PROV.wasInformedBy, None))
        self.remove((None, PROV.wasInformedBy, process[0]))
        self.remove((process[0], PROV.wasAssociatedWith, None))
        self.set((process[0], RDF.type, GEOKUR.SubProcess))

        self.remove((neighbor[0], PROV.wasInformedBy, None))
        self.remove((None, PROV.wasInformedBy, neighbor[0]))   
        self.remove((None, PROV.wasAssociatedWith, neighbor[0]))            
        self.set((neighbor[0], RDF.type, GEOKUR.SubProcess))

        # delete any intermediate data from graph
        for data in intermediateData:
            self.remove((data[0], None, None))
            self.remove((None, None, data[0]))

        # generate new process and links
        # naming convention: combined proc is named after higher importance subprocess
        # i.e. the neighbor
        newProcess = self.addProcess(str(neighbor[1]))
        self.add((newProcess, GEOKUR.hasRelativeImportance, Literal(float(neighbor[2]) + float(process[2]))))
        
        # add the 'old' processes again to the graph, but as subprocesses
        self.add((newProcess, GEOKUR.hasSubProcess, process[0]))
        self.add((newProcess, GEOKUR.hasSubProcess, neighbor[0]))

        self.link(
            inputs = [k[0] for k in inputData],
            process = newProcess,
            outputs = [k[0] for k in outputData],
            agents = [k[0] for k in associatedAgents]
        )
        for outP in outgoingProcesses:
            self.add((outP[0], PROV.wasInformedBy, newProcess))
        
        for inP in ingoingProcesses:
            self.add((newProcess, PROV.wasInformedBy, inP[0]))
        # print([str(k[1]) for k in inputData])
        # print([str(k[1]) for k in outputData])
        # print([str(k[1]) for k in intermediateData])
        # print([str(k[1]) for k in ingoingProcesses])
        # print([str(k[1]) for k in outgoingProcesses])

    def generalize(self, destination=None, format='xml'):           
            # print(len([k for k in self.triples((None, RDF.type, GEOKUR.Process))]))
            process, neighbor = self.getMergePair()
            self.merge(process, neighbor)
            self.serialize(format = format, destination = destination)
            print('Wrote graph to "' + destination + '".')
            self.mergeCount += 1
            

