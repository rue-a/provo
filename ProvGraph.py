from rdflib import Graph, Literal, BNode, URIRef, Namespace
from rdflib.namespace import DC, FOAF, RDF, RDFS
from rdflib.plugins.sparql import prepareQuery
import pandas as pd


# setup namespaces
PROV = Namespace("http://www.w3.org/ns/prov#")
GEOKUR =  Namespace("https://geokur.geo.tu-dresden.de/")


class ProvGraph(Graph):
    CHANGES = [
        GEOKUR.BasalChange, 
        GEOKUR.UnitChange,
        GEOKUR.ValueChange,
        GEOKUR.SemanticShift,
        GEOKUR.CoreConcept
    ]
    def __init__(self, store='default', identifier=None, namespace_manager=None):
        super().__init__(store=store, identifier=identifier, namespace_manager=namespace_manager)
        self.add((GEOKUR.Process, RDFS.subClassOf, PROV.Activity))
        self.add((GEOKUR.Data, RDFS.subClassOf, PROV.Entity))
        self.add((GEOKUR.hasProcessType, RDF.type, RDF.Property))
    # methods for construction of the prov graph
    def addProcess(self,  ID, processType):
        # if not processType:
        #     print(str(ID) + ": No process type declared, defaults to Informational Change.")
        #     processType = GEOKUR.InformationalChange
        self.add((ID, RDF.type, GEOKUR.Process))
        self.add((ID, GEOKUR.hasProcessType, processType))
    def addData(self, ID):
        self.add((ID, RDF.type, GEOKUR.Data))
    def addAgent(self, ID):
        self.add((ID, RDF.type, PROV.Agent))
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
    # methods for generating different granularities
    def serializeGranularities(self, name):
        # serialize in ground truth
        LOG = 0
        serializationName = name + '_LOG' + str(LOG) + '.rdf'
        self.serialize(format = 'n3', destination = serializationName)
        LOG += 1

        for index, changeType in enumerate(self.CHANGES):
            # --- flat merge
            mergeList = self.__getMergeList_Flat(changes = changeType)
            mergeLists = self.__divideMergeList(mergeList)
            self.__mergeParts(mergeLists, changeType)
            
            serializationName = name + '_LOG' + str(LOG) + '.rdf'
            self.serialize(format = 'n3', destination = serializationName)
            LOG += 1

            # --- up merge
            if index < len(self.CHANGES)-1: 
                mergeList = self.__getMergeList_Up(changes = changeType, changesUp = self.CHANGES[index + 1])
                subIndex = index
                while ((not mergeList) and (subIndex >= 0)):
                    subIndex -= 1
                    mergeList = self.__getMergeList_Up(changes = self.CHANGES[subIndex], changesUp = self.CHANGES[index + 1])
                
                mergeLists = self.__divideMergeList(mergeList)
                self.__mergeParts(mergeLists = mergeLists, changes = self.CHANGES[index + 1])
                
                serializationName = name + '_LOG' + str(LOG) + '.rdf'
                self.serialize(format = 'n3', destination = serializationName)
                LOG += 1

    
    def __mergeParts(self, mergeLists, changes):
        for lst in mergeLists:
            initializingProcs, finalizingProc, intermediateProcs = self.__getInitialAndFinalProcs(lst)
            # not very beautiful way of solving this / there are not root processes on stage two

            rootProcesses = self.__getRootProcs(initializingProcs=initializingProcs, intermediateProcs=intermediateProcs, changes = changes)

            sources = self.__getNewSources(rootProcs = rootProcesses, intermediateProcs = intermediateProcs, initializingProcs = initializingProcs)
            derivations = self.__getDerivationPaths(sources, finalizingProc)
            agents = self.__getAgents(intermediateProcs, initializingProcs)
            # construct new derivations            
            for row in derivations:
                # print(derivations)
                self.add((row[0], PROV.wasDerivedFrom, row[1]))
            # remove intermediate procs and their output:
            for process in (initializingProcs + intermediateProcs):
                self.__cleanFromIntermediateData(process)
                self.remove((process, None, None))
                self.remove((None,None,process))
                # print(process)
                
            # add new relations
            # (outputs don't change)
            
            self.link(
                inputs = sources,
                process = finalizingProc,
                agents = agents
            )
            # adjust process type
            self.remove((finalizingProc, GEOKUR.hasProcessType, None))
            self.add((finalizingProc, GEOKUR.hasProcessType, changes))
            
            


            # add wasInformedBy
            qRes = self.query(
            """
            SELECT ?p ?pp
            WHERE {
                ?p prov:used ?data .
                ?data prov:wasGeneratedBy ?pp .
            }
            """
            )
            for row in qRes:
                self.add((row[0], PROV.wasInformedBy, row[1]))
            

    
    
    def __getMergeList_Flat(self, changes):
        mergeQuery = prepareQuery(
            """
            SELECT
            ?sourceProcess ?rel ?process

            WHERE
            {
                ?process geokur:hasProcessType ?changes .
                ?sourceProcess prov:wasInformedBy ?process .
                ?sourceProcess geokur:hasProcessType ?changes .
                ?sourceProcess ?rel ?process .
            }
            """,
            initNs = { 
                "prov": PROV, 
                "geokur": GEOKUR
            }
        )

        branchQuery = prepareQuery(
            """
            SELECT ?process
            WHERE 
            {
                ?process prov:wasInformedBy ?currentProcess .
            }
            """,
            initNs = { "prov": PROV}
        )
        branchAnnotation = prepareQuery(
            """
            SELECT
                ?node
            WHERE {
                ?currentProc geokur:hasBranch "True"
            }
            """,
            
            initNs = { 
                "prov": PROV, 
                "geokur": GEOKUR
            }
            
        )

        mergeProcesses = []
        for row in self.query(mergeQuery, initBindings = {'changes': changes}):
            branches = self.query(branchQuery, initBindings={'currentProcess': row[2]})
            if not(len(branches) > 1):
                mergeProcesses.append((row[0], row[2]))
            else:
                if not len(self.query(branchAnnotation, initBindings={'currentProcess': row[2]}))>0:
                    self.add((row[2], GEOKUR.hasBranch, Literal('True')))
            #     print('graph branches on: ' + str(row[2]))
            # print(result)

        # items that only appear on the right part of the tuples in this list
        # are 'sources' of this subgraph. items that are only on the left side
        # are 'results'.
        return mergeProcesses


    def __getMergeList_Up(self, changes, changesUp):
        mergeQuery = prepareQuery(
            """
            SELECT
            ?sourceProcess ?rel ?process

            WHERE
            {
                {
                    ?process geokur:hasProcessType ?changesUp .
                    ?sourceProcess prov:wasInformedBy ?process .
                    ?sourceProcess geokur:hasProcessType ?changes .
                    ?sourceProcess ?rel ?process .
                }
                UNION
                {
                    ?process geokur:hasProcessType ?changes .
                    ?sourceProcess prov:wasInformedBy ?process .
                    ?sourceProcess geokur:hasProcessType ?changesUp .
                    ?sourceProcess ?rel ?process .
                }
            }
            """,
            initNs = { 
                "prov": PROV, 
                "geokur": GEOKUR
            }
        )

        branchQuery = prepareQuery(
            """
            SELECT ?process
            WHERE 
            {
                ?process prov:wasInformedBy ?currentProcess .
            }
            """,
            initNs = { "prov": PROV}
        )
        branchAnnotation = prepareQuery(
            """
            SELECT
                ?node
            WHERE {
                ?currentProc geokur:hasBranch "True"
            }
            """,
            
            initNs = { 
                "prov": PROV, 
                "geokur": GEOKUR
            }
            
        )

        mergeProcesses = []
        for row in self.query(mergeQuery, initBindings = {'changes': changes, 'changesUp': changesUp}):
            branches = self.query(branchQuery, initBindings={'currentProcess': row[2]})
            if not(len(branches) > 1):
                mergeProcesses.append((row[0], row[2]))
            else:
                if not len(self.query(branchAnnotation, initBindings={'currentProcess': row[2]}))>0:
                    self.add((row[2], GEOKUR.hasBranch, Literal('True')))
            #     print('graph branches on: ' + str(row[2]))
            # print(result)

        # items that only appear on the right part of the tuples in this list
        # are 'sources' of this subgraph. items that are only on the left side
        # are 'results'.
        return mergeProcesses

    def __divideMergeList(self, mergeList):
        # print(mergeList.pop(0))
        dividedLists = []
        while len(mergeList) > 0:
            item = mergeList.pop()
            dividedList = [item]
            for item in dividedList:
                for tupl in reversed(mergeList):
                    # check for overlap
                    lst = list(tupl)
                    lst.extend(list(item))
                    if len(set(lst)) < 4:
                        dividedList.append(tupl)
                        mergeList.remove(tupl)
            dividedLists.append(dividedList)
        return dividedLists


    def __getInitialAndFinalProcs(self, lst):
        # in the merge lists: left item in tuples are out, right are in
        # ( (a,b) means: a wasInformedBy b)
        # items that are only left but not on the right side in any tuple are 
        # final results, vice versa items only on the right, but not on the left 
        # side are sources of the regarding subgraph
        sources = []
        results = []
        intermediates = []
        df = pd.DataFrame.from_records(lst, columns = ['out', 'in'])
        for index, row in enumerate(df['in'].isin(df['out'])):
            if row:
                intermediates.append(df['in'][index])
            else:
                sources.append(df['in'][index])
        for index, row in enumerate(df['out'].isin(df['in'])):
            if row:
                intermediates.append(df['out'][index])
            else:
                results.append(df['out'][index])
        sources = list(set(sources))
        results = list(set(results))
        intermediates = list(set(intermediates))
        # result is always a single process - per definition
        return sources, results[0], intermediates

    def __getRootProcs(self, initializingProcs, intermediateProcs, changes):
        findRoots = prepareQuery(
            """
            SELECT
                ?root
            WHERE {
                {
                    ?process prov:wasInformedBy ?root .
                    MINUS {
                        ?process prov:wasInformedBy ?root .
                        ?root geokur:hasProcessType ?changes .
                    }
                } UNION
                {
                    ?process prov:wasInformedBy ?root .
                    ?root geokur:hasBranch "True" . 
                }
            }
            """,
            initNs = { 
                "prov": PROV, 
                "geokur": GEOKUR
            }
        )
        rootProcs = []
        for process in intermediateProcs + initializingProcs:
            for row in self.query(findRoots, initBindings= {'process': process, 'changes': changes}):
                rootProcs.append(row[0])
        return list(set(rootProcs))

    def __getNewSources(self, rootProcs, intermediateProcs, initializingProcs):
        findSources = prepareQuery(
            """
            SELECT
                ?node
            WHERE
            {
                ?process ?rel ?node 
                FILTER (
                    ?rel IN (prov:used)
                )
            }
            """,
            initNs = { 
                "prov": PROV, 
                "geokur": GEOKUR
            }
        )
        findMoreSources = prepareQuery(
            """
            SELECT
                ?source
            WHERE
            {
                ?source prov:wasGeneratedBy ?process.
            }
            """,
            initNs = { 
                "prov": PROV, 
                "geokur": GEOKUR
            }
        )
        sources = []
        for process in intermediateProcs + initializingProcs:
            for row in self.query(findSources, initBindings = {'process': process}):
                sources.append(row[0])
        for process in rootProcs:
            for row in self.query(findMoreSources, initBindings = {'process': process}):
                sources.append(row[0])
        
        return sources

    def __cleanFromIntermediateData(self, process):
        orphans = prepareQuery(
            """
            SELECT DISTINCT
            ?orphan
            WHERE{
                ?orphan prov:wasGeneratedBy ?process .
            }
            """,
            initNs = { 
                "prov": PROV, 
                "geokur": GEOKUR
            }
        )
        for row in self.query(orphans, initBindings = {'process': process}):
            print(row[0])
            self.remove((row[0], None, None))
            self.remove((None, None, row[0]))
        
                
    
    def __getDerivationPaths(self, sources, finalizingProcess):
        getDerivationPath = prepareQuery(
            """
            SELECT
            ?finalData ?sourceData
            WHERE{
                ?finalData prov:wasGeneratedBy ?finalizingProcess .
                ?finalData prov:wasDerivedFrom* ?sourceData .

            }
            """,
            initNs = { 
                "prov": PROV, 
                "geokur": GEOKUR
            }
        )
        derivations = []
        for source in sources:
            for row in self.query(getDerivationPath, initBindings = {'sourceData': source, 'finalizingProcess': finalizingProcess}):
                derivations.append(row)    
        return derivations

    def __getAgents(self, intermediateProcs, initializingProcs):
        getAgent = prepareQuery(
            """
            SELECT ?agent
            WHERE{
                ?process prov:wasAssociatedWith ?agent
            }
            """,
            initNs = { 
                "prov": PROV, 
                "geokur": GEOKUR
            }
        )
        agents = []
        for process in (intermediateProcs + initializingProcs):
            for row in self.query(getAgent, initBindings = {'process': process}):
                agents.append(row[0])
        return agents