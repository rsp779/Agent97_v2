from pathlib import Path

from src.data.data_access_layer import DataAccessLayer


def test_relationships_are_resolved():
    dal = DataAccessLayer.from_path(Path("output/small"))
    row = dal.get_by_id("accounts", "acc_00000001")
    assert row is not None
    parent = dal.parent("accounts", "acc_00000001", "customer_id", "customers")
    assert parent is not None

