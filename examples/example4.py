from ProvIt import ProvenanceEngine

# define your methods
def add(x, y):
    # add two numbers
    z = x + y
    return z

def subtract(x,y):
    # subtract two numbers
    z = x - y
    return z

# setup the provenance engine object and provide it with a namespace
provEngine = ProvenanceEngine(
    namespace = 'https://usefulmodulecollection.org/modul1#', 
    abbreviation = 'm1'
)

meID = provEngine.setupDefaultPerson(
    label = 'Me',
    description = '... (could possibly be left out)',
    OrcID = 'https://orcid.org/0000-0001-8637-9071'
)

a = 4
aID = provEngine.addEntity(
    label = 'Variable A',
    description = "it's value is: " + str(a)
)


b = 5
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


# add another person and it's organization
testPersonID = provEngine.addAgent(
    label = 'testPerson',
    OrcID = 'https://this-is-no-orcID.org/'
)

organizationID = provEngine.addAgent(
    label = 'organization',
    description = 'all people work here'
)

# relate me and the test person to the organization
provEngine.relatePersonsAndOrganizations(
    personIDs = [meID, testPersonID],
    organizationIDs = organizationID
)

d = subtract(a,b)
# add the result as entity.
dID = provEngine.addEntity('Variable C', 'A - B = ' + str(d))

# add the process to the graph
# provide this process with an agentID, this overwrites the default agent for 
# this process
subID = provEngine.addProcess(
    label = 'subtract',
    description = 'subtracts two numbers',
    agentID = testPersonID
)
provEngine.relateProcessAndEntities(
    inputIDs = [aID,bID],
    outputIDs = dID,
    processID = subID
)


# save the graph in the Turtle format
provEngine.serialize('example4.ttl')