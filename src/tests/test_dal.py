from pathlib import Path

from src.data.data_access_layer import DataAccessLayer


def test_dal_lazy_load_and_indexes():
    dal = DataAccessLayer.from_path(Path("output/small"))
    customer = dal.get_by_id("customers", "cus_00000001")
    assert customer is not None
    assert dal.count("customers") > 0
    assert dal.exists("customers", customer_id="cus_00000001")
    accounts = dal.children("customers", "cus_00000001")
    assert "accounts" in accounts

