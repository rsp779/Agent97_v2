from __future__ import annotations

from collections import defaultdict

from src.models.datasets import FraudAlert, FraudCase

from .banking_repository import BankingRepository
from .customer_repository import CustomerRepository
from .digital_repository import DigitalRepository
from .transaction_repository import TransactionRepository


class FraudRepository:
    def __init__(self, dal) -> None:
        self.dal = dal
        self.customer_repository = CustomerRepository(dal)
        self.banking_repository = BankingRepository(dal)
        self.digital_repository = DigitalRepository(dal)
        self.transaction_repository = TransactionRepository(dal)

    def get_open_alerts(self) -> list[FraudAlert]:
        return [FraudAlert.model_validate(row) for row in self.dal.find("fraud_alerts", alert_status="open")]

    def get_high_risk_alerts(self) -> list[FraudAlert]:
        return [FraudAlert.model_validate(row) for row in self.dal.find("fraud_alerts", severity="high")]

    def get_customer_cases(self, customer_id: str) -> list[FraudCase]:
        return [FraudCase.model_validate(row) for row in self.dal.find("fraud_cases", customer_id=customer_id)]

    def get_confirmed_cases(self, customer_id: str) -> list[FraudCase]:
        return [case for case in self.get_customer_cases(customer_id) if case.case_status == "confirmed"]

    def get_mule_network(self, customer_id: str) -> list[dict]:
        return self.dal.filter("mule_networks", lambda row: row.get("source_customer_id") == customer_id or row.get("target_customer_id") == customer_id)

    def get_linked_customers(self, customer_id: str) -> list[str]:
        linked = set()
        for row in self.get_mule_network(customer_id):
            linked.add(row["source_customer_id"])
            linked.add(row["target_customer_id"])
        linked.discard(customer_id)
        return sorted(linked)

    def build_investigation_package(self, customer_id: str) -> dict[str, list | dict]:
        customer = self.customer_repository.get_customer(customer_id)
        if customer is None:
            return {}
        accounts = self.banking_repository.get_customer_accounts(customer_id)
        devices = self.digital_repository.get_customer_devices(customer_id)
        sessions = self.digital_repository.get_customer_sessions(customer_id)
        account_ids = {account.account_id for account in accounts}
        device_ids = {device.device_id for device in devices}
        session_ids = {session.session_id for session in sessions}
        alert_ids = set()
        case_ids = set()
        alerts = []
        cases = []
        investigations = []
        transactions = [row for row in self.dal.load_dataset("transactions") if row["account_id"] in account_ids]
        for row in self.dal.load_dataset("fraud_alerts"):
            if row["customer_id"] == customer_id:
                alerts.append(row)
                alert_ids.add(row["fraud_alert_id"])
        for row in self.dal.load_dataset("fraud_cases"):
            if row["customer_id"] == customer_id or row["fraud_alert_id"] in alert_ids:
                cases.append(row)
                case_ids.add(row["fraud_case_id"])
        for row in self.dal.load_dataset("investigations"):
            if row["fraud_case_id"] in case_ids:
                investigations.append(row)
        return {
            "customer": customer.model_dump(),
            "accounts": [account.model_dump() for account in accounts],
            "transactions": transactions,
            "devices": [device.model_dump() for device in devices],
            "sessions": [session.model_dump() for session in sessions],
            "alerts": alerts,
            "cases": cases,
            "investigations": investigations,
        }

