"""
@author Arne Rümmler
@contact arne.ruemmler@gmail.com

@summary Implementation of the starting term classes of
 PROV-O https://www.w3.org/TR/prov-o/ .
"""


from dataclasses import dataclass, field
from uuid import uuid4
from validators import url


@dataclass(frozen=True)
class IdMalformed(Exception):
    """Raised when a node id is invalid."""

    message: str


@dataclass(frozen=True)
class IdAlreadyUsed(Exception):
    """Raised when a node with an id that already exists is created."""

    message: str


@dataclass
class IdVault:
    """manages unique IDs and generates new ones"""

    vault: list[str] = field(init=False, default_factory=list)
    _invalid_symbols: str = field(init=False, default='<>" {}|\\^`')

    def _raise_exception_if_uri_invalid(self, uri: str) -> None:
        "checks if uri is valid and raises exception if not"

        # TODO rethink validation, we technically want to validate an IRI
        if not url(uri):  # type: ignore
            raise IdMalformed(
                """
            The provided namespace is not a valid URL!

            See validators package (https://github.com/python-validators/validators),
            validators.url() or https://gist.github.com/dperini/729294 for more
            information on what qualifies a URL as valid.
            
            https://www.rfc-editor.org/rfc/rfc3986#section-3:
            3.  Syntax Components

            The generic URI syntax consists of a hierarchical sequence of
            components referred to as the scheme, authority, path, query, and
            fragment.

                URI         = scheme ":" hier-part [ "?" query ] [ "#" fragment ]

                hier-part   = "//" authority path-abempty
                            / path-absolute
                            / path-rootless
                            / path-empty

            The scheme and path components are required, though the path may be
            empty (no characters).  When authority is present, the path must
            either be empty or begin with a slash ("/") character.  When
            authority is not present, the path cannot begin with two slash
            characters ("//").  These restrictions result in five different ABNF
            rules for a path (Section 3.3), only one of which will match any
            given URI reference.

            The following are two example URIs and their component parts:

                    foo://example.com:8042/over/there?name=ferret#nose
                    \_/   \______________/\_________/ \_________/ \__/
                    |           |            |            |        |
                scheme     authority       path        query   fragment
                    |   _____________________|__
                    / \ /                        \
                    urn:example:animal:ferret:nose
            """
            )

    def generate(self, namespace: str) -> str:
        """generates a new uuid that is not in the vault yet"""
        node_id = namespace + str(uuid4())
        while node_id in self.vault:
            node_id = namespace + str(uuid4())
        self._raise_exception_if_uri_invalid(node_id)
        self.vault.append(node_id)
        return node_id

    def add_id(self, node_id: str) -> str:
        """adds a user defined id and checks if its valid"""
        if node_id in self.vault:
            raise IdAlreadyUsed(
                f'The Id "{node_id}" was already used in this graph.')
        print(node_id)
        self._raise_exception_if_uri_invalid(node_id)
        self.vault.append(node_id)
        return node_id
