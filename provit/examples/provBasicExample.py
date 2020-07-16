
from provit import ProvGraph, Activity, Entity, Agent

''' setup the graph object (subclass of an rdflib-graph)'''
g = ProvGraph(namespace='https://provBasicExample.org/')


'''at first we create all required objects'''
inputEntity = Entity(graph = g, id = 'inputEntity')
# any PROV-O object can have a label and a description
inputEntity.label('Input Entity')
inputEntity.description('This is the first entity')

outputEntity = Entity(g, 'outputEntity')

activity = Activity(g, 'activity')

agent = Agent(g, 'agent')


'''now we build the relations'''
activity.used(inputEntity)
activity.wasAssociatedWith(agent)
outputEntity.wasGeneratedBy(activity)
outputEntity.wasAttributedTo(agent)
outputEntity.wasDerivedFrom(inputEntity)


'''finally serialize the graph'''

path = 'provit/examples/out/provBasicExample_n3.rdf'
g.serialize(format = 'n3', destination = path)