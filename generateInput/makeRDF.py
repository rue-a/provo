# %%
import prov.model as prov
import datetime

doc = prov.ProvDocument.deserialize(source='gnatcatcher.rdf', format='rdf')

print(doc.get_provn())

doc.serialize(destination = 'gnatcatcher.xml', format = 'xml')