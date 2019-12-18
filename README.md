# ProvIt

__--- IN DEVELOPMENT ---__

*This package aims at supporting the tracking of provenance of Python-scripted workflows as an RDF-Graph (semantic graph), according to the PROV-Ontology.*

*A future tool will allow for a meaningful visualization of provenance stored in a fashion this package provides.*

*While the ProvIt-Package tries to enable the tracking of provenance without further knowledge of semantic graph databases or the PROV-Ontology the End of this document provides some  foundational concepts.*

## Getting started

The package assumes that a certain workflow is constructed out of a set of processes with well defined inputs and outputs. Such a process is typically written down as a method:

```python
def add(x,y):
    z = x + y
    return z

a = 4
b = 5
c = add(a,b)
```

In this simple case the process is the addition of two numbers.