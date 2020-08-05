# %%
import prov.model as prov
import datetime
import xml.etree.ElementTree as et
import random

documentName = 'gnatcatcher'

# convert from rdf to provXML
doc = prov.ProvDocument.deserialize(source = documentName + '.rdf', format='rdf')
doc.serialize(destination = documentName + '.xml', format = 'xml')


# add graph drawing information

# et.register_namespace(prefix = 'xmlns:graph', uri ='https://jgraph.github.io/mxgraph/')
tree = et.parse(documentName + '.xml')

root = tree.getroot()
root.attrib = {
    'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'xmlns:graph':'https://jgraph.github.io/mxgraph/'}

# get all sub elements (former root.getchildren())
resources = list(root.iter())

indexDict = {}
for index, resource in enumerate(resources):
    element = et.Element('graph:information')
    element.attrib = {'graph:id': str(index)}
    # indexDict[resource.attrib]
    if (resource.attrib):
        indexDict[str((list(resource.attrib.values()))[0])] = str(index)
    resource.append(element)

for resource in resources:
    # print(resource.tag)
    for graphInfo in resource.findall('graph:information'):
        if resource.tag in [
            '{http://www.w3.org/ns/prov#}entity',
            '{http://www.w3.org/ns/prov#}activity',
            '{http://www.w3.org/ns/prov#}agent']:
            element = et.Element('mxCell')
            if resource.tag == '{http://www.w3.org/ns/prov#}entity':
                element.attrib = {
                    'style': 'dataDMP',
                    'parent': str(1),
                    'vertex': str(1)
                }
            if resource.tag == '{http://www.w3.org/ns/prov#}activity':
                element.attrib = {
                    'style': 'processDMP',
                    'parent': str(1),
                    'vertex': str(1)
                }
            if resource.tag == '{http://www.w3.org/ns/prov#}agent':
                element.attrib = {
                    'style': 'actorDMP',
                    'parent': str(1),
                    'vertex': str(1)
                }
            graphInfo.append(element)
            for mxCell in graphInfo.findall('mxCell'):
                element = et.Element('mxGeometry')
                element.attrib = {
                    'x':str(random.randint(-1000,1000)),
                    'y':str(random.randint(-1000,1000)) ,
                    'width':"170",
                    'height':"40",
                    'as':"geometry"
                }
                mxCell.append(element)

        if resource.tag in [
            '{http://www.w3.org/ns/prov#}used',
            '{http://www.w3.org/ns/prov#}wasGeneratedBy',
            '{http://www.w3.org/ns/prov#}wasDerivedFrom',
            '{http://www.w3.org/ns/prov#}wasInformedBy'
        ]:
           
            origin = resource.findall('{http://www.w3.org/ns/prov#}usedEntity')
            target = resource.findall('{http://www.w3.org/ns/prov#}generatedEntity')
            if not origin:
                origin = resource.findall('{http://www.w3.org/ns/prov#}informant')
                target = resource.findall('{http://www.w3.org/ns/prov#}informed')
            if not origin:
                if resource.tag == '{http://www.w3.org/ns/prov#}used':
                    origin = resource.findall('{http://www.w3.org/ns/prov#}entity')
                    target = resource.findall('{http://www.w3.org/ns/prov#}activity')
                if resource.tag == '{http://www.w3.org/ns/prov#}wasGeneratedBy':
                    origin = resource.findall('{http://www.w3.org/ns/prov#}activity')
                    target = resource.findall('{http://www.w3.org/ns/prov#}entity')
            source = indexDict.get(next(iter(origin[0].attrib.values())))
            destination = indexDict.get(next(iter(target[0].attrib.values())))

            element = et.Element('mxCell')
            element.attrib = {
                'parent':"1",
                'source':source,
                'target':destination,
                'edge':"1"
            }
            graphInfo.append(element)

            mxCell = graphInfo.find('mxCell')
            element = et.Element('mxGeometry')
            element.attrib = {
                'relative': str(1),
                'as': 'geometry'
            }
            mxCell.append(element)

            geom = mxCell.find('mxGeometry')
            element = et.Element('Array')
            element.attrib = {
                'as': 'points'
            }
            geom.append(element)
            
            array = geom.find('Array')
            element = et.Element('mxPoint')
            element.attrib = {
                'x': '1',
                'y': '1'
            }
            array.append(element)


        if resource.tag in [
            '{http://www.w3.org/ns/prov#}wasAssociatedWith',
            '{http://www.w3.org/ns/prov#}wasAttributedTo'
        ]:

            origin = resource.find('{http://www.w3.org/ns/prov#}agent')
            source = indexDict.get(next(iter(origin.attrib.values())))
            # source = indexDict.get([list(agent.attrib.values())[0] for agent in agents][0])
            
            target = resource.findall('{http://www.w3.org/ns/prov#}entity')
            if not target:
                target = resource.findall('{http://www.w3.org/ns/prov#}activity')           
            destination = indexDict.get(next(iter(target[0].attrib.values())))
            element = et.Element('mxCell')
            element.attrib = {
                'style':"shape=connector;fontSize=10;align=center;verticalAlign=middle;rounded=1;labelBackgroundColor=white;strokeColor=#727675;strokeWidth=1;edgeStyle=elbowEdgeStyle;endArrow=openThin;html=1;dashed=1;jettySize=auto;orthogonalLoop=1;startArrow=oval",
                'parent':"1",
                'source':source,
                'target':destination,
                'edge':"1"
            }
            graphInfo.append(element)

            mxCell = graphInfo.find('mxCell')
            element = et.Element('mxGeometry')
            element.attrib = {
                'relative': str(1),
                'as': 'geometry'
            }
            mxCell.append(element)

            geom = mxCell.find('mxGeometry')
            element = et.Element('Array')
            element.attrib = {
                'as': 'points'
            }
            geom.append(element)

            array = geom.find('Array')
            element = et.Element('mxPoint')
            element.attrib = {
                'x': '1',
                'y': '1'
            }
            array.append(element)


tree.write(documentName + 'Graph.xml')