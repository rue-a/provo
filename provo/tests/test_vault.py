import pytest
from provo.idvault import IdAlreadyUsed, IdInvalid, IdVault
from validators import url


def test_generate():
    """tests if the automatically generated id is a valid url"""

    namespace = "https://test.package/"
    vault = IdVault()
    id = vault.generate(namespace=namespace)
    # TODO rethink validation
    assert url(id)  # type: ignore


def test_no_id_duplication():
    """tests if vault throws IdAlreadyUsed exception when an existing
    id is added to the vault"""

    namespace = "https://test.package/"
    test_id = "test"
    vault = IdVault()
    vault.add_id(node_id=test_id)
    with pytest.raises(IdAlreadyUsed):
        vault.add_id(node_id=test_id)


def test_id_validation():
    """tests if vault throws IdInvalid exception if id contains one
    of the invalid symbols"""

    vault = IdVault()
    invalid_symbols = '<>" {}|\\^`'

    for symbol in invalid_symbols:
        # test if error is thrown if namespace contains the symbol
        namespace = f"https://t{symbol}est.package/"
        test_id = "test"
        with pytest.raises(IdInvalid):
            vault._raise_exception_if_uri_invalid(namespace + test_id)

        # test if error is thrown if id without namespace contains the symbol
        namespace = "https://test.package/"
        test_id = f"te{symbol}st"
        with pytest.raises(IdInvalid):
            vault._raise_exception_if_uri_invalid(namespace + test_id)
