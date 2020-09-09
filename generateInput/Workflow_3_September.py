from provit import ProvGraph, Activity, Entity, Agent

# setup the graph object (subclass of an rdflib-graph)
g = ProvGraph(namespace='https://gnatcatcher.org/')


censusStat = Entity(g, 'censusStats')
censusStat.description('content of table: brutto area (C, F), netto area (C), yield (C), production (C), headcount (L), animal units (L)')
geometries = Entity(g, 'geometries')
geometries.description('content of table: spatial extent of admin units')
pointRecords = Entity(g, 'pointRecords')
pointRecords.description('content of table: coordinates, land-use type')
arealDB = Entity(g, 'arealDB')
rectifyR = Activity(g, 'rectifyR')
xyz = Agent(g, 'XYZ')
liang = Agent(g, 'Liang')
navin = Agent(g, 'Navin')
felipe = Agent(g, 'Felipe')
steffen_f = Agent(g, 'Steffen_F')
katharina = Agent(g, 'Katharina')
steffen = Agent(g, 'Steffen')
ruben = Agent(g, 'Ruben')
giuseppe = Agent(g, 'Giuseppe')
g.link(
    inputs = [censusStat, geometries, pointRecords],
    process = rectifyR,
    outputs = arealDB,
    agents = [xyz, liang, navin, felipe, steffen_f, katharina, ruben, steffen, giuseppe] 
)

naming = Activity(g, 'naming')
carsten = Agent(g, 'Carsten')
g.link(
    inputs = None,
    process = naming,
    outputs = arealDB,
    agents = [steffen, carsten]
)

originalRSData = Entity(g, 'rawRSData')
standardisedRSData = Entity(g, 'standardisedRSData')
dataPrep = Activity(g, 'dataPreparation')
g.link(
    inputs = originalRSData,
    process = dataPrep, 
    outputs = standardisedRSData,
    agents = [steffen, giuseppe]
)

g.link(
    inputs = None,
    process = naming,
    outputs = standardisedRSData,
    agents = [steffen, carsten]
)

geoRegistration = Activity(g, 'GeoRegistration')
spatialDB = Entity(g, 'spatialDB')
g.link(
    inputs = arealDB,
    process = geoRegistration,
    outputs = spatialDB,
    agents = [ruben, steffen, giuseppe]
)

qualLayers = Entity(g, 'qualityLayers')
modelling = Activity(g, 'modelling')
tentativeOutput = Entity(g, 'tentativeOutput')
marius = Agent(g, 'Marius')
peter = Agent(g, 'Peter')
daniele = Agent(g, 'Daniele')
longzhu = Agent(g, 'Longzhu')
g.link(
    inputs = [spatialDB, standardisedRSData, qualLayers],
    process = modelling,
    outputs = tentativeOutput,
    agents = [carsten, marius, peter, steffen, daniele, katharina, longzhu, giuseppe]
)

qualDeterm = Activity(g, 'qualityDetermination')
g.link(
    inputs = tentativeOutput,
    process = qualDeterm,
    outputs = qualLayers,
    agents = [steffen, carsten]
)

provDocumentation = Activity(g, 'provenanceDocumentation')
provLayers = Entity(g, 'provenanceLayers')
lars = Agent(g, 'Lars')
stephan = Agent(g, 'Stephan')
g.link(
    inputs = [arealDB, standardisedRSData, tentativeOutput],
    process = provDocumentation,
    outputs = provLayers,
    agents = [steffen, lars, carsten, stephan]
)

postConsAnalysis = Activity(g, 'postConsistencyAnalysis')
dataLayers = Entity(g, 'DataLayers')
g.link(
    inputs = tentativeOutput,
    process = postConsAnalysis,
    outputs = dataLayers,
    agents = [steffen, carsten]
)

path = 'geokur.ttl'
g.serialize(format = 'ttl', destination = path)