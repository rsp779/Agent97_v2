from pathlib import Path

from src.data.data_access_layer import DataAccessLayer


def test_indexing_reuses_primary_key():
    dal = DataAccessLayer.from_path(Path("output/small"))
    first = dal.get_by_id("transactions", "txn_00000001")
    second = dal.get("transactions", transaction_id="txn_00000001")
    assert first == second

