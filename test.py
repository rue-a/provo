from ProvIt import ProvenanceEngine
from ProvIt import utilities


def inner_test(input, inputID):
    # do coll things with the input
    output = input + '! That was great.'
    
    outID = provenanceEngine.addEntity(
    localIdentifier = 'output',
    description = 'description of the resource'
    )


    procID = provenanceEngine.addProcess(        
        inputIDs = inputID,
        outputIDs = outID,
        description = 'puhh tl;dr'
        )
    
    return (output, outID)


def test_func(a ,aID, b , bID):

    # do
    # something
    # meaningful
    # with
    # a
    # and
    # b
    # here

    c = a+b

    cID = provenanceEngine.addEntity(
        localIdentifier = 'output',
        description = 'really exhausting description of the resource'
        )
    final = inner_test(input = c, inputID = cID)

    
    procID = provenanceEngine.addProcess(
        inputIDs = [aID, bID],
        outputIDs = final[1],
        label = 'process name',
        description = 'tl;dr',
        processType = 'structural'
        )
    return final[0]
    
    


provenanceEngine = ProvenanceEngine()

provenanceEngine.setupAttributedPerson('me', "it's me", 'really!', 'LokNaRash')

aID = provenanceEngine.addEntity(
    localIdentifier = 'input1', 
    label = '1st input', 
    description = 'quite exhausting description of the resource'
    )
bID = provenanceEngine.addEntity(
    localIdentifier = 'input2', 
    label = '2st input', 
    description = 'exhausting description of the resource'
    )
result = test_func(a = 'inputA', aID = aID, b = 'inputB', bID = bID)
print(result)

# provenanceEngine.addEntity(
#     localIdentifier = 'input2', 
#     description = 'exhausting description of the resource'
# )
# provenanceEngine.addEntity(
#     localIdentifier = 'output', 
#     description = 'exhausting description of the resource'
# )

provenanceEngine.serialize('test.ttl')