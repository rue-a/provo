
import pytest

from provo.provontologygraph import (NamespaceHasNoEndSymbol,
                                     NamespaceMalformed, PrefixNotAllowed,
                                     PrefixShorthandNotValid,
                                     ProvOntologyGraph)


def test_graph_initialization():
    """tests if namespace and namespace abbreviation (i.e., prefix) is valid"""
    
    ProvOntologyGraph()
    ProvOntologyGraph(default_namespace="https://test.package/", namespace_abbreviation="")
    ProvOntologyGraph(default_namespace="https://test.package#", namespace_abbreviation="")

    malformed_namespaces = ["www.test.de", "https://test.package/ ",
                            "test.org", " https://test.package/"]
    for namespace in malformed_namespaces:
        with pytest.raises(NamespaceMalformed):
            ProvOntologyGraph(default_namespace=namespace)

    with pytest.raises(NamespaceHasNoEndSymbol):
        ProvOntologyGraph(default_namespace="https://test.package")

    invalid_prefixes = [" ", ":", "test:"]
    for prefix in invalid_prefixes:
        with pytest.raises(PrefixShorthandNotValid):
            ProvOntologyGraph(namespace_abbreviation=prefix)

    core_prefixes = ["owl", "rdf", "rdfs", "xsd", "xml"]
    for prefix in core_prefixes:
        with pytest.raises(PrefixNotAllowed):
            ProvOntologyGraph(namespace_abbreviation=prefix)
