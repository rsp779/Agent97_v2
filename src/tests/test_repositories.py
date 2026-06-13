from pathlib import Path

from src.repositories.factory import RepositoryFactory


def test_factory_and_investigation_package():
    repos = RepositoryFactory.create(Path("output/small"))
    customer = repos.customer_repository.get_customer("cus_00000001")
    assert customer is not None
    package = repos.fraud_repository.build_investigation_package("cus_00000001")
    assert set(package) == {"customer", "accounts", "transactions", "devices", "sessions", "alerts", "cases", "investigations"}

