from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Any

from .base import BaseToolService, ToolSpec
from .schemas import (
    AlertTimelineInput,
    BehavioralAnomalyInput,
    CaseSummaryInput,
    CustomerFraudSummaryInput,
    FraudAlertsInput,
    FraudCaseInput,
    HighRiskEntitiesInput,
    InvestigationPackageInput,
    MuleNetworkInput,
    VelocityAnomalyInput,
)
from .schemas import ToolResponse


FRAUD_TOOL_SPECS = (
    ToolSpec("get_fraud_alerts", "Return fraud alerts.", FraudAlertsInput, "get_fraud_alerts"),
    ToolSpec("get_fraud_case", "Return a fraud case.", FraudCaseInput, "get_fraud_case"),
    ToolSpec("get_case_summary", "Return a fraud case summary.", CaseSummaryInput, "get_case_summary"),
    ToolSpec("get_investigation_package", "Return an investigation package.", InvestigationPackageInput, "get_investigation_package"),
    ToolSpec("get_customer_fraud_summary", "Return a customer fraud summary.", CustomerFraudSummaryInput, "get_customer_fraud_summary"),
    ToolSpec("get_alert_timeline", "Return an alert timeline.", AlertTimelineInput, "get_alert_timeline"),
    ToolSpec("get_mule_network", "Return mule network data.", MuleNetworkInput, "get_mule_network"),
    ToolSpec("get_high_risk_entities", "Return high risk entities.", HighRiskEntitiesInput, "get_high_risk_entities"),
    ToolSpec("detect_velocity_anomalies", "Detect velocity anomalies.", VelocityAnomalyInput, "detect_velocity_anomalies"),
    ToolSpec("detect_behavioral_anomalies", "Detect behavioral anomalies.", BehavioralAnomalyInput, "detect_behavioral_anomalies"),
)


class FraudTools(BaseToolService):
    repository_name = "fraud_repository"

    def get_fraud_alerts(self, input: FraudAlertsInput) -> ToolResponse:
        """Return fraud alerts with optional filtering."""

        def action() -> list[dict[str, Any]]:
            if input.customer_id:
                package = self.repositories.fraud_repository.build_investigation_package(input.customer_id)
                rows = package.get("alerts", [])
            else:
                rows = [alert.model_dump() for alert in self.repositories.fraud_repository.get_open_alerts()]
                rows.extend(alert.model_dump() for alert in self.repositories.fraud_repository.get_high_risk_alerts())
            results = []
            for row in rows:
                if input.severity and row.get("severity") != input.severity:
                    continue
                if input.alert_status and row.get("alert_status") != input.alert_status:
                    continue
                results.append(row)
            return results

        return self._execute(
            tool_name="get_fraud_alerts",
            repository_used=self.repository_name,
            success_message="fraud alerts retrieved",
            action=action,
        )

    def get_fraud_case(self, input: FraudCaseInput) -> ToolResponse:
        """Return a fraud case by id or customer."""

        def action() -> dict[str, Any]:
            if input.customer_id:
                cases = self.repositories.fraud_repository.get_customer_cases(input.customer_id)
            else:
                cases = [case.model_dump() for customer in self.repositories.customer_repository.get_customers() for case in self.repositories.fraud_repository.get_customer_cases(customer.customer_id)]
            for case in cases:
                if input.fraud_case_id is None or case.get("fraud_case_id") == input.fraud_case_id:
                    return case
            return {}

        return self._execute(
            tool_name="get_fraud_case",
            repository_used=self.repository_name,
            success_message="fraud case retrieved",
            action=action,
        )

    def get_case_summary(self, input: CaseSummaryInput) -> ToolResponse:
        """Return a summary for a fraud case."""

        def action() -> dict[str, Any]:
            case = self.get_fraud_case(FraudCaseInput(customer_id=input.customer_id, fraud_case_id=input.fraud_case_id))
            if not case.success or not case.data:
                return {}
            case_data = case.data if isinstance(case.data, dict) else {}
            customer_id = case_data.get("customer_id", input.customer_id)
            package = self.repositories.fraud_repository.build_investigation_package(customer_id) if customer_id else {}
            return {
                "fraud_case": case_data,
                "alerts": len(package.get("alerts", [])),
                "investigations": len(package.get("investigations", [])),
                "linked_customers": self.repositories.fraud_repository.get_linked_customers(customer_id) if customer_id else [],
            }

        return self._execute(
            tool_name="get_case_summary",
            repository_used=self.repository_name,
            success_message="case summary retrieved",
            action=action,
        )

    def get_investigation_package(self, input: InvestigationPackageInput) -> ToolResponse:
        """Return the normalized investigation package."""

        return self._execute(
            tool_name="get_investigation_package",
            repository_used=self.repository_name,
            success_message="investigation package retrieved",
            action=lambda: self.repositories.fraud_repository.build_investigation_package(input.customer_id),
        )

    def get_customer_fraud_summary(self, input: CustomerFraudSummaryInput) -> ToolResponse:
        """Return a compact fraud summary for a customer."""

        def action() -> dict[str, Any]:
            package = self.repositories.fraud_repository.build_investigation_package(input.customer_id)
            return {
                "customer_id": input.customer_id,
                "alerts": len(package.get("alerts", [])),
                "cases": len(package.get("cases", [])),
                "investigations": len(package.get("investigations", [])),
                "linked_customers": self.repositories.fraud_repository.get_linked_customers(input.customer_id),
            }

        return self._execute(
            tool_name="get_customer_fraud_summary",
            repository_used=self.repository_name,
            success_message="customer fraud summary retrieved",
            action=action,
        )

    def get_alert_timeline(self, input: AlertTimelineInput) -> ToolResponse:
        """Return a chronological alert timeline."""

        def action() -> list[dict[str, Any]]:
            package = self.repositories.fraud_repository.build_investigation_package(input.customer_id)
            alerts = package.get("alerts", [])
            alerts.sort(key=lambda row: str(row.get("created_at", "")))
            return alerts

        return self._execute(
            tool_name="get_alert_timeline",
            repository_used=self.repository_name,
            success_message="alert timeline retrieved",
            action=action,
        )

    def get_mule_network(self, input: MuleNetworkInput) -> ToolResponse:
        """Return mule network links for a customer."""

        return self._execute(
            tool_name="get_mule_network",
            repository_used=self.repository_name,
            success_message="mule network retrieved",
            action=lambda: self.repositories.fraud_repository.get_mule_network(input.customer_id),
        )

    def get_high_risk_entities(self, input: HighRiskEntitiesInput) -> ToolResponse:
        """Return a compact list of high risk entities."""

        def action() -> list[dict[str, Any]]:
            rows: list[dict[str, Any]] = []
            if input.customer_id:
                package = self.repositories.fraud_repository.build_investigation_package(input.customer_id)
                rows.extend(package.get("alerts", []))
                rows.extend(package.get("cases", []))
            else:
                for alert in self.repositories.fraud_repository.get_high_risk_alerts():
                    rows.append(alert.model_dump())
            rows.sort(key=lambda row: str(row.get("created_at", row.get("opened_at", ""))))
            return rows[: input.limit or 10]

        return self._execute(
            tool_name="get_high_risk_entities",
            repository_used=self.repository_name,
            success_message="high risk entities retrieved",
            action=action,
        )

    def detect_velocity_anomalies(self, input: VelocityAnomalyInput) -> ToolResponse:
        """Detect simple velocity anomalies."""

        def action() -> dict[str, Any]:
            velocity = self.repositories.transaction_repository.get_transaction_velocity(input.customer_id, hours=input.hours or 24)
            return {
                "customer_id": input.customer_id,
                "velocity": velocity,
                "threshold": input.threshold or 10,
                "anomaly_detected": velocity >= (input.threshold or 10),
            }

        return self._execute(
            tool_name="detect_velocity_anomalies",
            repository_used="transaction_repository",
            success_message="velocity anomalies evaluated",
            action=action,
        )

    def detect_behavioral_anomalies(self, input: BehavioralAnomalyInput) -> ToolResponse:
        """Detect simple behavioral anomalies from signal counts."""

        def action() -> dict[str, Any]:
            profile = self.repositories.digital_repository.get_behavioral_profile(input.customer_id)
            total = sum(profile.values())
            max_signal = max(profile.values()) if profile else 0
            anomaly = bool(profile) and max_signal > max(1, total // 2)
            return {"customer_id": input.customer_id, "behavioral_profile": profile, "anomaly_detected": anomaly}

        return self._execute(
            tool_name="detect_behavioral_anomalies",
            repository_used="digital_repository",
            success_message="behavioral anomalies evaluated",
            action=action,
        )

