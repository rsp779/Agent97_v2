from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

from .base import BaseToolService, ToolSpec
from .schemas import (
    LargeTransactionsInput,
    RecentTransactionsInput,
    SpendingByCategoryInput,
    SpendingSummaryInput,
    TransactionDetailsInput,
    TransactionNetworkInput,
    TransactionSearchInput,
    TransactionTimelineInput,
    VelocityMetricsInput,
)
from .schemas import ToolResponse


TRANSACTION_TOOL_SPECS = (
    ToolSpec("get_recent_transactions", "Return recent transactions for a customer.", RecentTransactionsInput, "get_recent_transactions"),
    ToolSpec("search_transactions", "Search transactions by filters.", TransactionSearchInput, "search_transactions"),
    ToolSpec("get_transaction_details", "Return a transaction detail record.", TransactionDetailsInput, "get_transaction_details"),
    ToolSpec("get_spending_summary", "Return spending summary for a customer.", SpendingSummaryInput, "get_spending_summary"),
    ToolSpec("get_spending_by_category", "Return spending grouped by merchant/category proxy.", SpendingByCategoryInput, "get_spending_by_category"),
    ToolSpec("get_velocity_metrics", "Return transaction velocity metrics.", VelocityMetricsInput, "get_velocity_metrics"),
    ToolSpec("get_large_transactions", "Return large transactions for a customer.", LargeTransactionsInput, "get_large_transactions"),
    ToolSpec("get_transaction_network", "Return a transaction network summary.", TransactionNetworkInput, "get_transaction_network"),
    ToolSpec("get_transaction_timeline", "Return a transaction timeline.", TransactionTimelineInput, "get_transaction_timeline"),
)


class TransactionTools(BaseToolService):
    repository_name = "transaction_repository"

    def _customer_transactions(self, customer_id: str):
        return self.repositories.transaction_repository.get_customer_transactions(customer_id)

    def _all_transactions(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for customer in self.repositories.customer_repository.get_customers():
            rows.extend(txn.model_dump() for txn in self._customer_transactions(customer.customer_id))
        return rows

    def get_recent_transactions(self, input: RecentTransactionsInput) -> ToolResponse:
        """Return transactions in the recent time window."""

        return self._execute(
            tool_name="get_recent_transactions",
            repository_used=self.repository_name,
            success_message="recent transactions retrieved",
            action=lambda: [txn.model_dump() for txn in self.repositories.transaction_repository.get_recent_transactions(input.customer_id, days=input.days or 30)],
        )

    def search_transactions(self, input: TransactionSearchInput) -> ToolResponse:
        """Search transactions across customers using normalized filters."""

        def action() -> list[dict[str, Any]]:
            rows = self._all_transactions() if input.customer_id is None else [txn.model_dump() for txn in self._customer_transactions(input.customer_id)]
            cutoff = None
            if input.days is not None:
                cutoff = datetime.now(timezone.utc) - timedelta(days=input.days)
            results: list[dict[str, Any]] = []
            for row in rows:
                if cutoff is not None and row["transaction_time"] < cutoff:
                    continue
                if input.merchant_name and input.merchant_name.lower() not in str(row.get("merchant_id", "")).lower():
                    continue
                if input.amount_min is not None and row["amount"] < input.amount_min:
                    continue
                if input.amount_max is not None and row["amount"] > input.amount_max:
                    continue
                if input.transaction_type and row.get("transaction_type") != input.transaction_type:
                    continue
                if input.status and row.get("status") != input.status:
                    continue
                results.append(row)
            return results

        return self._execute(
            tool_name="search_transactions",
            repository_used=self.repository_name,
            success_message="transaction search completed",
            action=action,
        )

    def get_transaction_details(self, input: TransactionDetailsInput) -> ToolResponse:
        """Return a single transaction by id."""

        def action() -> dict[str, Any]:
            if input.customer_id:
                rows = [txn.model_dump() for txn in self._customer_transactions(input.customer_id)]
            else:
                rows = self._all_transactions()
            for row in rows:
                if row["transaction_id"] == input.transaction_id:
                    return row
            return {}

        return self._execute(
            tool_name="get_transaction_details",
            repository_used=self.repository_name,
            success_message="transaction details retrieved",
            action=action,
        )

    def get_spending_summary(self, input: SpendingSummaryInput) -> ToolResponse:
        """Return a customer spending summary."""

        def action() -> dict[str, Any]:
            txns = self.repositories.transaction_repository.get_recent_transactions(input.customer_id, days=input.days or 30)
            return {
                "customer_id": input.customer_id,
                "transaction_count": len(txns),
                "total_spend": round(sum(txn.amount for txn in txns if txn.status != "declined"), 2),
                "average_transaction": round(sum(txn.amount for txn in txns) / len(txns), 2) if txns else 0.0,
            }

        return self._execute(
            tool_name="get_spending_summary",
            repository_used=self.repository_name,
            success_message="spending summary retrieved",
            action=action,
        )

    def get_spending_by_category(self, input: SpendingByCategoryInput) -> ToolResponse:
        """Return grouped spend using merchant id as the category proxy."""

        def action() -> dict[str, Any]:
            txns = self.repositories.transaction_repository.get_recent_transactions(input.customer_id, days=input.days or 30)
            grouped: dict[str, float] = defaultdict(float)
            for txn in txns:
                grouped[txn.merchant_id or "unknown"] += txn.amount
            return {"customer_id": input.customer_id, "categories": [{"category": key, "amount": round(value, 2)} for key, value in grouped.items()]}

        return self._execute(
            tool_name="get_spending_by_category",
            repository_used=self.repository_name,
            success_message="spending by category retrieved",
            action=action,
        )

    def get_velocity_metrics(self, input: VelocityMetricsInput) -> ToolResponse:
        """Return transaction velocity metrics."""

        def action() -> dict[str, Any]:
            hours = input.hours or 24
            txns = self.repositories.transaction_repository.get_recent_transactions(input.customer_id, days=max(1, hours // 24 or 1))
            return {
                "customer_id": input.customer_id,
                "velocity_24h": self.repositories.transaction_repository.get_transaction_velocity(input.customer_id, hours=hours),
                "recent_count": len(txns),
            }

        return self._execute(
            tool_name="get_velocity_metrics",
            repository_used=self.repository_name,
            success_message="velocity metrics retrieved",
            action=action,
        )

    def get_large_transactions(self, input: LargeTransactionsInput) -> ToolResponse:
        """Return transactions above a configurable amount."""

        return self._execute(
            tool_name="get_large_transactions",
            repository_used=self.repository_name,
            success_message="large transactions retrieved",
            action=lambda: [txn.model_dump() for txn in self.repositories.transaction_repository.get_high_value_transactions(input.customer_id, minimum=input.minimum or 50000)[: input.limit or 10]],
        )

    def get_transaction_network(self, input: TransactionNetworkInput) -> ToolResponse:
        """Return a light-weight transaction network summary."""

        def action() -> dict[str, Any]:
            txns = self.repositories.transaction_repository.get_customer_transactions(input.customer_id)
            counterparties = Counter(txn.counterparty_account_id for txn in txns if txn.counterparty_account_id)
            merchants = Counter(txn.merchant_id for txn in txns if txn.merchant_id)
            return {
                "customer_id": input.customer_id,
                "counterparties": [{"account_id": key, "count": value} for key, value in counterparties.most_common()],
                "merchants": [{"merchant_id": key, "count": value} for key, value in merchants.most_common()],
            }

        return self._execute(
            tool_name="get_transaction_network",
            repository_used=self.repository_name,
            success_message="transaction network retrieved",
            action=action,
        )

    def get_transaction_timeline(self, input: TransactionTimelineInput) -> ToolResponse:
        """Return a chronological transaction timeline."""

        def action() -> list[dict[str, Any]]:
            cutoff = datetime.now(timezone.utc) - timedelta(days=input.days or 30)
            rows = [txn.model_dump() for txn in self.repositories.transaction_repository.get_customer_transactions(input.customer_id) if txn.transaction_time >= cutoff]
            rows.sort(key=lambda row: row["transaction_time"])
            return rows

        return self._execute(
            tool_name="get_transaction_timeline",
            repository_used=self.repository_name,
            success_message="transaction timeline retrieved",
            action=action,
        )

