from pathlib import Path

from src.repositories.factory import RepositoryFactory


def test_investigation_package_shape():
    repos = RepositoryFactory.create(Path("output/small"))
    package = repos.fraud_repository.build_investigation_package("cus_00000001")
    assert isinstance(package["customer"], dict)
    assert isinstance(package["accounts"], list)
    assert isinstance(package["transactions"], list)

