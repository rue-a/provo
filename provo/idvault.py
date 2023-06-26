"""
@author Arne Rümmler
@contact arne.ruemmler@gmail.com

@summary Implementation of the starting term classes of
 PROV-O https://www.w3.org/TR/prov-o/ .
"""


from dataclasses import dataclass, field
from uuid import uuid4


@dataclass(frozen=True)
class IdInvalid(Exception):
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

        for symbol in uri:
            if symbol in self._invalid_symbols:
                raise IdInvalid(f"The Id \"{uri}\" is invalid (contains one or more of: \033[1m{self._invalid_symbols}\033[0m).")

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
            raise IdAlreadyUsed(f'The Id "{node_id}" was already used in this graph.')
        self._raise_exception_if_uri_invalid(node_id)
        self.vault.append(node_id)
        return node_id
