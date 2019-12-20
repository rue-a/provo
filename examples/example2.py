from ProvIt import ProvenanceEngine

# define your methods
def add(x, y):
    # add two numbers
    z = x + y
    return z

# setup the provenance engine object and provide it with a namespace
provEngine = ProvenanceEngine(
    namespace = 'https://usefulmodulecollection.org/modul1#', 
    abbreviation = 'm1'
)


# add the process to the graph
procID = provEngine.addProcess(
    label = 'add',
    description = 'adds two numbers and gives out a sum'
)


# define lists
A = [4,4,8]
B = [1,2,3]

# add the elements and construct the according entities and 
# relations between them on the flow

C = []
for i in range(3):
    a = A[i]
    aID = provEngine.addEntity(
        label = 'Variable a',        
        description = "its value is: " + str(a)
    )

    b = B[i]
    bID = provEngine.addEntity(
        label = 'Variable b',
        description = "its value is: " + str(b)
    )

    c = add(a,b)
    cID = provEngine.addEntity('Variable c', 'a + b = ' + str(c))
    C.append(c)

    # connect the nodes
    provEngine.relateProcessAndEntities(
        inputIDs = [aID,bID],
        outputIDs = cID,
        processID = procID
    )

# save the graph in the Turtle format
provEngine.serialize('example2.ttl')