# README

## Installation

1. Download and extract the package
2. Open Shell and _cd_ to extracted package
3. Run "pip install -e ." (in the folder that contains setup.py)

## Contents

The package implements the PROV-O (https://www.w3.org/TR/prov-o/#starting-points-figure) classes __Entity__, __Activity__ and __Agent__ as Python classes with methods to establish the basic relations between those classes. It also contains utilities to construct provenance graphs with less typing.

## Functionality

The folder _examples_ provides an example document that features the serialization a an ArcGIS Workflow into a provenance graph. The folder _out_ contains this graph. The tutorial containing the example workflwo can be found under: http://webhelp.esri.com/arcgisdesktop/9.3/pdf/Geoprocessing_in_ArcGIS_Tutorial.pdf, p. 36ff.