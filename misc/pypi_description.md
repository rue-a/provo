The package supports the creation of [PROV-O](https://www.w3.org/TR/prov-o/) compliant provenance graphs. 

The package requires __Python 3.11__.

## Installation

You can install the package from the Python Package Index (PyPI):

`pip install provo`

## Contents

The package implements the [PROV-O starting point classes](https://www.w3.org/TR/prov-o/#starting-points-figure) __Entity__, __Activity__ and __Agent__ as Python classes with methods to establish starting point properties between them instances of these classes. 

## Features

### Compliance

- The PROV-O classes __Entity__, __Activity__, and __Agent__ are implemented as Python classes.
- The PROV-O properties _wasGeneratedBy_, _wasDerivedFrom_, _wasAttributedTo_, _startedAtTime_, _used_, _wasInformedBy_, _endedAtTime_, _wasAssociatedWith_, and _actedOnBehalfOf_ are implemented as instance methods of their according classes.
- Attributes that are passes to these methods are type-checked to enforce compliance with PROV-O.
itemName=ms-python.vscode-pylance).
- Node Ids are checked for validity.
- Accidental use of the same ID for different objects throws an error.

### Ease of Use

- The package implements full type hint support, thus enabling rich support from linters such as [Pylance](https://marketplace.visualstudio.com/items).
- The classes `Provence_Ontology_Graph`, `Entity`, `Activity`, and `Agent` can be printed to terminal in a user-friendly, readable way with the default `print()` command.

- for some quick testing, objects of the classes `Entity`, `Activity`, and `Agent` can be instantiated with auto-generated Ids (although it's not recommended using this for production).

### Interface to RDF via the [rdflib](https://rdflib.readthedocs.io/en/stable/) package

- The graph's contents can be converted to an `rdflib.Graph` object.
- The graph can be exported in various RDF serializations.