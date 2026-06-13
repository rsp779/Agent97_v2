from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone

from src.models.datasets import Transaction


class TransactionRepository:
    def __init__(self, dal) -> None:
        self.dal = dal

    def get_customer_transactions(self, customer_id: str) -> list[Transaction]:
        account_ids = {row["account_id"] for row in self.dal.find("accounts", customer_id=customer_id)}
        rows = [row for row in self.dal.load_dataset("transactions") if row["account_id"] in account_ids]
        return [Transaction.model_validate(row) for row in rows]

    def get_recent_transactions(self, customer_id: str, days: int = 30) -> list[Transaction]:
        threshold = datetime.now(timezone.utc) - timedelta(days=days)
        return [txn for txn in self.get_customer_transactions(customer_id) if txn.transaction_time >= threshold]

    def get_total_spend(self, customer_id: str) -> float:
        return round(sum(txn.amount for txn in self.get_customer_transactions(customer_id) if txn.status != "declined"), 2)

    def get_average_transaction(self, customer_id: str) -> float:
        txns = self.get_customer_transactions(customer_id)
        return round(sum(txn.amount for txn in txns) / len(txns), 2) if txns else 0.0

    def get_transaction_velocity(self, customer_id: str, hours: int = 24) -> int:
        threshold = datetime.now(timezone.utc) - timedelta(hours=hours)
        return sum(1 for txn in self.get_customer_transactions(customer_id) if txn.transaction_time >= threshold)

    def get_high_value_transactions(self, customer_id: str, minimum: float = 50000) -> list[Transaction]:
        return [txn for txn in self.get_customer_transactions(customer_id) if txn.amount >= minimum]

    def get_top_merchants(self, customer_id: str, limit: int = 5) -> list[tuple[str, int]]:
        counts = Counter(txn.merchant_id for txn in self.get_customer_transactions(customer_id))
        return counts.most_common(limit)

