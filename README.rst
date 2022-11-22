README
======

The package supports the creation of
`PROV-O <https://www.w3.org/TR/prov-o/>`__ compliant provenance graphs.

The package requires **Python 3.11**.

Installation
------------

You can install the package from the Python Package Index (PyPI):

``pip install provo``

Contents
--------

The package implements the `PROV-O starting point
classes <https://www.w3.org/TR/prov-o/#starting-points-figure>`__
**Entity**, **Activity** and **Agent** as Python classes with methods to
establish starting point properties between them instances of these
classes.

Features
--------

The package's objective is it to support the programmatical creation 
of provenance graphs that are compliant with the W3C Recommendation 
PROV-O: The PROV Ontology. Users of the package shall be enabled to 
tightly couple the generation of data with the generation of their 
provenance. As the package implements PROV-O, the created graph is 
exportable as an RDF document.

Compliance
~~~~~~~~~~

-  The PROV-O classes **Entity**, **Activity**, and **Agent** are
   implemented as Python classes.
-  The PROV-O properties *wasGeneratedBy*, *wasDerivedFrom*,
   *wasAttributedTo*, *startedAtTime*, *used*, *wasInformedBy*,
   *endedAtTime*, *wasAssociatedWith*, and *actedOnBehalfOf* are
   implemented as instance methods of their according classes.
-  Attributes that are passed to these methods are type-checked to
   enforce compliance with PROV-O.
-  Node Ids are checked for validity.
-  (Accidental) use of the same ID for different objects throws an error.

Ease of Use
~~~~~~~~~~~

-  The package implements full type hint support, thus enabling rich
   support from the IDE.
-  The classes ``Provence_Ontology_Graph``, ``Entity``, ``Activity``,
   and ``Agent`` can be printed to terminal in a user-friendly, readable
   way with the default ``print()`` command.
-  For some quick testing, objects of the classes ``Entity``,
   ``Activity``, and ``Agent`` can be instantiated with auto-generated
   Ids (although it's not recommended using this for production).

Interface to RDF via the `rdflib <https://rdflib.readthedocs.io/en/stable/>`__ package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  The graph's contents can be converted to an ``rdflib.Graph`` object.
-  The graph can be exported in various RDF serializations.

Manual
------

https://github.com/rue-a/provo#manual
