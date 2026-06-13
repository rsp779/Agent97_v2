from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from .base import BaseToolService, ToolSpec
from .schemas import (
    CustomerContactInfoInput,
    CustomerNetworkInput,
    CustomerOverviewInput,
    CustomerProfileInput,
    CustomerRelationshipsInput,
    CustomerRiskSummaryInput,
    CustomerSearchInput,
    CustomerTimelineInput,
)
from .schemas import ToolResponse


CUSTOMER_TOOL_SPECS = (
    ToolSpec("get_customer_profile", "Return a normalized customer profile.", CustomerProfileInput, "get_customer_profile"),
    ToolSpec("get_customer_network", "Return the customer network context.", CustomerNetworkInput, "get_customer_network"),
    ToolSpec("get_customer_relationships", "Return the customer relationships extracted from linked entities.", CustomerRelationshipsInput, "get_customer_relationships"),
    ToolSpec("get_customer_risk_summary", "Return a customer risk summary.", CustomerRiskSummaryInput, "get_customer_risk_summary"),
    ToolSpec("search_customer", "Search customers by text or segment filters.", CustomerSearchInput, "search_customer"),
    ToolSpec("get_customer_contact_info", "Return customer contact details.", CustomerContactInfoInput, "get_customer_contact_info"),
    ToolSpec("get_customer_overview", "Return a full customer overview.", CustomerOverviewInput, "get_customer_overview"),
    ToolSpec("get_customer_timeline", "Return a combined customer timeline.", CustomerTimelineInput, "get_customer_timeline"),
)


class CustomerTools(BaseToolService):
    repository_name = "customer_repository"

    def _customer(self, customer_id: str):
        return self.repositories.customer_repository.get_customer(customer_id)

    def get_customer_profile(self, input: CustomerProfileInput) -> ToolResponse:
        """Return the customer profile for a single customer."""

        return self._execute(
            tool_name="get_customer_profile",
            repository_used=self.repository_name,
            success_message="customer profile retrieved",
            action=lambda: self._customer(input.customer_id).model_dump() if self._customer(input.customer_id) else None,
        )

    def get_customer_network(self, input: CustomerNetworkInput) -> ToolResponse:
        """Return the network view for a customer."""

        return self._execute(
            tool_name="get_customer_network",
            repository_used=self.repository_name,
            success_message="customer network retrieved",
            action=lambda: self.repositories.customer_repository.get_customer_network(input.customer_id),
        )

    def get_customer_relationships(self, input: CustomerRelationshipsInput) -> ToolResponse:
        """Return linked customer relationships derived from the network context."""

        def action() -> dict[str, Any]:
            network = self.repositories.customer_repository.get_customer_network(input.customer_id)
            relationships: list[dict[str, Any]] = []
            for account in network.get("accounts", []):
                relationships.append({"type": "account", "id": account.get("account_id"), "customer_id": input.customer_id})
            for card in network.get("cards", []):
                relationships.append({"type": "card", "id": card.get("credit_card_id"), "customer_id": input.customer_id})
            for device in network.get("devices", []):
                relationships.append({"type": "device", "id": device.get("device_id"), "customer_id": input.customer_id})
            for session in network.get("sessions", []):
                relationships.append({"type": "session", "id": session.get("session_id"), "customer_id": input.customer_id})
            return {"customer_id": input.customer_id, "relationships": relationships}

        return self._execute(
            tool_name="get_customer_relationships",
            repository_used=self.repository_name,
            success_message="customer relationships retrieved",
            action=action,
        )

    def get_customer_risk_summary(self, input: CustomerRiskSummaryInput) -> ToolResponse:
        """Return a normalized customer risk summary."""

        def action() -> dict[str, Any]:
            customer = self._customer(input.customer_id)
            if customer is None:
                return {}
            banking = self.repositories.banking_repository
            digital = self.repositories.digital_repository
            transaction = self.repositories.transaction_repository
            return {
                "customer_id": input.customer_id,
                "risk_segment": customer.risk_segment,
                "total_exposure": banking.get_total_exposure(input.customer_id),
                "total_balance": banking.get_total_balance(input.customer_id),
                "device_risk": digital.get_device_risk(input.customer_id),
                "transaction_velocity_24h": transaction.get_transaction_velocity(input.customer_id, hours=24),
                "recent_spend": transaction.get_total_spend(input.customer_id),
            }

        return self._execute(
            tool_name="get_customer_risk_summary",
            repository_used="banking_repository/digital_repository/transaction_repository",
            success_message="customer risk summary retrieved",
            action=action,
        )

    def search_customer(self, input: CustomerSearchInput) -> ToolResponse:
        """Search customers using the repository bundle."""

        def action() -> list[dict[str, Any]]:
            customers = self.repositories.customer_repository.get_customers()
            query = (input.query or "").lower().strip()
            rows = []
            for customer in customers:
                record = customer.model_dump()
                if input.customer_id and record["customer_id"] != input.customer_id:
                    continue
                if input.city and record.get("city") != input.city:
                    continue
                if input.risk_segment and record.get("risk_segment") != input.risk_segment:
                    continue
                if query:
                    haystack = " ".join(str(record.get(key, "")) for key in ("customer_id", "full_name", "email", "phone", "city", "state", "risk_segment")).lower()
                    if query not in haystack:
                        continue
                rows.append(record)
            return rows

        return self._execute(
            tool_name="search_customer",
            repository_used=self.repository_name,
            success_message="customer search completed",
            action=action,
        )

    def get_customer_contact_info(self, input: CustomerContactInfoInput) -> ToolResponse:
        """Return contact information for a customer."""

        def action() -> dict[str, Any]:
            customer = self._customer(input.customer_id)
            if customer is None:
                return {}
            return {
                "customer_id": customer.customer_id,
                "full_name": customer.full_name,
                "email": customer.email,
                "phone": customer.phone,
                "address_line1": customer.address_line1,
                "city": customer.city,
                "state": customer.state,
                "postal_code": customer.postal_code,
                "country": customer.country,
            }

        return self._execute(
            tool_name="get_customer_contact_info",
            repository_used=self.repository_name,
            success_message="customer contact info retrieved",
            action=action,
        )

    def get_customer_overview(self, input: CustomerOverviewInput) -> ToolResponse:
        """Return a customer overview with risk and activity context."""

        def action() -> dict[str, Any]:
            customer = self._customer(input.customer_id)
            if customer is None:
                return {}
            network = self.repositories.customer_repository.get_customer_network(input.customer_id)
            fraud_package = self.repositories.fraud_repository.build_investigation_package(input.customer_id)
            return {
                "profile": customer.model_dump(),
                "banking": {
                    "accounts": len(network.get("accounts", [])),
                    "cards": len(network.get("cards", [])),
                    "loans": len(self.repositories.banking_repository.get_customer_loans(input.customer_id)),
                    "balance": self.repositories.banking_repository.get_total_balance(input.customer_id),
                    "exposure": self.repositories.banking_repository.get_total_exposure(input.customer_id),
                },
                "digital": self.repositories.digital_repository.get_session_summary(input.customer_id),
                "fraud": {
                    "alerts": len(fraud_package.get("alerts", [])),
                    "cases": len(fraud_package.get("cases", [])),
                    "investigations": len(fraud_package.get("investigations", [])),
                },
            }

        return self._execute(
            tool_name="get_customer_overview",
            repository_used="customer_repository/banking_repository/digital_repository/fraud_repository",
            success_message="customer overview retrieved",
            action=action,
        )

    def get_customer_timeline(self, input: CustomerTimelineInput) -> ToolResponse:
        """Return a combined activity timeline for a customer."""

        def action() -> list[dict[str, Any]]:
            customer = self._customer(input.customer_id)
            if customer is None:
                return []
            cutoff = None
            if input.days is not None:
                cutoff = datetime.now(timezone.utc) - timedelta(days=input.days)
            events: list[dict[str, Any]] = []
            for transaction in self.repositories.transaction_repository.get_customer_transactions(input.customer_id):
                if cutoff is None or transaction.transaction_time >= cutoff:
                    events.append({"type": "transaction", "id": transaction.transaction_id, "ts": transaction.transaction_time.isoformat(), "amount": transaction.amount})
            for session in self.repositories.digital_repository.get_customer_sessions(input.customer_id):
                if cutoff is None or session.login_at >= cutoff:
                    events.append({"type": "session", "id": session.session_id, "ts": session.login_at.isoformat(), "channel": session.channel})
            package = self.repositories.fraud_repository.build_investigation_package(input.customer_id)
            for alert in package.get("alerts", []):
                events.append({"type": "fraud_alert", "id": alert.get("fraud_alert_id"), "ts": alert.get("created_at"), "severity": alert.get("severity")})
            for case in package.get("cases", []):
                events.append({"type": "fraud_case", "id": case.get("fraud_case_id"), "ts": case.get("opened_at"), "status": case.get("case_status")})
            for item in package.get("investigations", []):
                events.append({"type": "investigation", "id": item.get("investigation_id"), "ts": item.get("started_at"), "status": item.get("status")})
            events.sort(key=lambda row: str(row.get("ts", "")))
            return events

        return self._execute(
            tool_name="get_customer_timeline",
            repository_used="transaction_repository/digital_repository/fraud_repository",
            success_message="customer timeline retrieved",
            action=action,
        )
