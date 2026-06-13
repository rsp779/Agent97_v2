from __future__ import annotations

import json
from pathlib import Path


RELATIONSHIPS = {
    "accounts": [("customer_id", "customers", "customer_id")],
    "credit_cards": [("customer_id", "customers", "customer_id"), ("account_id", "accounts", "account_id")],
    "loans": [("customer_id", "customers", "customer_id"), ("account_id", "accounts", "account_id")],
    "devices": [("customer_id", "customers", "customer_id")],
    "sessions": [("customer_id", "customers", "customer_id"), ("device_id", "devices", "device_id")],
    "behavioral_signals": [("session_id", "sessions", "session_id"), ("device_id", "devices", "device_id")],
    "account_openings": [("customer_id", "customers", "customer_id"), ("account_id", "accounts", "account_id")],
    "kyc_documents": [("customer_id", "customers", "customer_id")],
    "transactions": [("account_id", "accounts", "account_id"), ("counterparty_account_id", "accounts", "account_id"), ("credit_card_id", "credit_cards", "credit_card_id"), ("merchant_id", "merchants", "merchant_id")],
    "fraud_alerts": [("transaction_id", "transactions", "transaction_id"), ("customer_id", "customers", "customer_id")],
    "fraud_cases": [("fraud_alert_id", "fraud_alerts", "fraud_alert_id"), ("customer_id", "customers", "customer_id")],
    "mule_networks": [("fraud_case_id", "fraud_cases", "fraud_case_id"), ("source_customer_id", "customers", "customer_id"), ("target_customer_id", "customers", "customer_id")],
    "investigations": [("fraud_case_id", "fraud_cases", "fraud_case_id")],
    "approvals": [("investigation_id", "investigations", "investigation_id")],
    "task_history": [("investigation_id", "investigations", "investigation_id")],
    "agent_feedback": [("task_history_id", "task_history", "task_history_id")],
}


def validate(output_dir: Path) -> list[str]:
    datasets = {}
    for path in output_dir.glob("*.json"):
        datasets[path.stem] = json.loads(path.read_text(encoding="utf-8"))
    errors = []
    for child, rules in RELATIONSHIPS.items():
        for fk, parent, pk in rules:
            parent_ids = {row[pk] for row in datasets.get(parent, [])}
            for row in datasets.get(child, []):
                if row[fk] not in parent_ids:
                    errors.append(f"{child}.{fk} references missing {parent}.{pk}: {row[fk]}")
    return errors
