from datetime import datetime
from provit import ProvGraph, Activity, Entity, Agent

g = ProvGraph(namespace='https://gnatcatcher.org/')

majorRoads = Entity(g, 'MajorRoads')
majorRoads.label('Major Roads')
majorRoads.description('major roads in the studies area')

buffer = Activity(g, 'Buffer')
buffer.label('ArcGIS Buffer')
buffer.description('20 m buffer around major roads')
# buffer.startedAtTime(datetime(2020, 6, 6, 12, 0, 0))
# buffer.endedAtTime(datetime(2020, 6, 6, 12, 4, 30))

roadsBuffer = Entity(g, 'RoadsBuffer')
roadsBuffer.label('Buffered Roads')

tom = Agent(g, 'Tom')
tom.label('Tom G.')
tom.description('Everyone knows Tom')

g.link(
    inputs=majorRoads, 
    process=buffer, 
    outputs=roadsBuffer,
    agents=tom
)

inputVeg = Entity(g, 'InputVegetation')
select = Activity(g, 'SelectVegetation')
suitableVeg = Entity( g, 'SuitableVegetation')
g.link(
    inputs=inputVeg, 
    process=select, 
    outputs=suitableVeg
)

erase = Activity(g, 'Erase')
suitMinusRoads = Entity(g, 'SuitableVegetationMinusRoads')
g.link(
    inputs=[suitableVeg, roadsBuffer],
    process=erase,
    outputs=suitMinusRoads
)

initialClimate = Entity(g, 'ClimateZones')
selClimate = Activity(g, 'SelectClimate')
climate = Entity(g, 'ClimateZonesSelection')
g.link(
    inputs=initialClimate,
    process=selClimate,
    outputs=climate
)

dem = Entity(g, 'DEM')
generateSlopes = Activity(g, 'Slope')
allSlopes = Entity(g, 'Slopes')
g.link(
    inputs=dem,
    process=generateSlopes,
    outputs=allSlopes
)

selectSlopes = Activity(g, 'SelectSlopes')
slopes = Entity(g, 'SlopesLessThan40Percent')
g.link(
    inputs=allSlopes,
    process=selectSlopes,
    outputs=slopes
)

selectElev = Activity(g, 'SelectElev')
elev = Entity(g, 'ElevationsLessThan250m')
g.link(
    inputs=dem,
    process=selectElev,
    outputs=elev
)


intersect = Activity(g, 'Intersect')
intersectOut = Entity(g, 'intersectOutput')
g.link(
    inputs=[elev, slopes, climate, suitMinusRoads],
    process=intersect,
    outputs=intersectOut
)

dissolve = Activity(g, 'dissolve')
dissOut = Entity(g, 'dissolveOutput')
g.link(
    inputs=intersectOut,
    process=dissolve,
    outputs=dissOut
)

multi = Activity(g, 'multipartToSinglepart')
singleOut = Entity(g, 'singlepartOutput')
g.link(
    inputs=dissOut,
    process=multi,
    outputs=singleOut
)

sel2 = Activity(g, 'SelectHabitats')
final = Entity(g, 'OutputPotentialHabitat')
g.link(
    inputs=singleOut,
    process=sel2,
    outputs=final
)



# path = '.provit/examples/out/gnatcatcher_xml.rdf'
# g.serialize(format = 'xml', destination = path)
path = 'provit/examples/out/gnatcatcher_extended.rdf'
g.serialize(format = 'ttl', destination = path)

