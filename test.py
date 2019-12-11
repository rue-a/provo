from ProvEngine import ProvenanceEngine

provenanceEngine = ProvenanceEngine()
provenanceEngine.addDataset(
    identifier = 'input1', 
    label = '1st input', 
    description = 'exhausting description of the resource'
)
provenanceEngine.addDataset(
    identifier = 'input2', 
    description = 'exhausting description of the resource'
)
provenanceEngine.addDataset(
    identifier = 'output', 
    description = 'exhausting description of the resource'
)
provenanceEngine.addProcess(
    identifier = 'testPrc',
    label = 'f',
    description = 'dd',
    type = 'structural'
)
provenanceEngine.trackProvenance(
    input = ['input1', 'input2'],
    process = 'testPrc',
    output = 'output'
)
provenanceEngine.printStuff()