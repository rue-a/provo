
import pytest
from provo.provontologygraph import (NamespaceHasNoEndSymbol,
                                     NamespaceMalformed,
                                     PrefixShorthandNotValid,
                                     ProvOntologyGraph)


def test_graph_initialization():
    # tests if namespace is valid url
    ProvOntologyGraph()
    ProvOntologyGraph(namespace="https://test.package/", namespace_abbreviation="")
    ProvOntologyGraph(namespace="https://test.package#", namespace_abbreviation="")

    with pytest.raises(NamespaceMalformed):
        ProvOntologyGraph(namespace="www.test.de")
    with pytest.raises(NamespaceMalformed):
        ProvOntologyGraph(namespace="test.org")
    with pytest.raises(NamespaceMalformed):
        ProvOntologyGraph(namespace="https://test.package/ ")
    with pytest.raises(NamespaceMalformed):
        ProvOntologyGraph(namespace=" https://test.package/")

    with pytest.raises(NamespaceHasNoEndSymbol):
        ProvOntologyGraph(namespace="https://test.package")

    with pytest.raises(PrefixShorthandNotValid):
        ProvOntologyGraph(namespace_abbreviation=" ")
    with pytest.raises(PrefixShorthandNotValid):
        ProvOntologyGraph(namespace_abbreviation=":")
    with pytest.raises(PrefixShorthandNotValid):
        ProvOntologyGraph(namespace_abbreviation="test:")
