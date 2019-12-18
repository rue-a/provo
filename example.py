# from ProvIt import ProvenanceEngine

# # define your methods
# def add(x, y):
#     # add two numbers
#     z = x + y
#     return z

# # setup the provenance engine object and provide it with a namespace
# # and it's abbreviation. It defaults to:
# # namespace = 'https://your.project.com/example#', abbreviation = 'ex'
# # every module should have it's own namespace
# provEngine = ProvenanceEngine(namespace = 'https://usefulmodulecollection.org/modul1#', abbreviation = 'm1')

# # the crucial part of the sematic graph are the unique IDs of every node.
# # you need to prevent duplicated localIdentifiers in the current scope of 
# # your python program. If you do the addEntity()-method will take care of
# # non-duplicated global Identifiers. Those global Identifiers are returned:
# aID = provEngine.addEntity(
#     localIdentifier = 'variableA'
# )
# a = 4

# # you can and should provide Entities with a human-readable label and a 
# # detailed description. If no label is provided it defaults to the global
# # identifier.
# bID = provEngine.addEntity(
#     localIdentifier = 'variableB',
#     label = 'Variable B',
#     description = 'The variable B is the 2nd summand of the equation.'
# )
# b = 5

# # While we don't know the sum yet, we know that there will be a sum.
# cID = provEngine.addEntity('varC', 'Variable C', 'The Sum of A and B.')

# c = add(a,b, aID, bID, cID, provEngine)
# # add the process to the graph and connect the nodes via ID
# provEngine.addProcess(
#     inputIDs = [aID, bID],
#     outputIDs = cID,
#     description = 'Add two Numbers'

# provEngine.serialize('module1.ttl')