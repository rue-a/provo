from ProvIt import ProvenanceEngine

# define your methods
def add(x, y):
    # add two numbers
    z = x + y
    return z

# setup the provenance engine object and provide it with a namespace
# and it's abbreviation. It defaults to:
# namespace = 'https://your.project.com/example#', abbreviation = 'ex'
# every module should have it's own namespace
provEngine = ProvenanceEngine(
    namespace = 'https://usefulmodulecollection.org/modul1#', 
    abbreviation = 'm1'
)


a = 4
# the crucial part of the sematic graph are the unique IDs of every node.
# These IDs are returned as you call the add*()-methods:
aID = provEngine.addEntity()


b = 5
# you can and should provide Entities with a human-readable label and a 
# detailed description. If no label is provided it defaults to the global
# identifier, which isn't meaningful (it's just unique).
bID = provEngine.addEntity(
    label = 'Variable B',
    description = "it's value is: " + str(b)
)


c = add(a,b)
# add the result as entity.
cID = provEngine.addEntity('Variable C', 'A + B = ' + str(c))


# add the process to the graph
procID = provEngine.addProcess(
    label = 'add',
    description = 'adds two numbers and gives out a sum'
)

# finally connect the nodes
provEngine.relateProcessAndEntities(
    inputIDs = [aID,bID],
    outputIDs = cID,
    processID = procID
)

# save the graph in the Turtle format
provEngine.serialize('example.ttl')