from __future__ import annotations

from collections.abc import Iterable


PRIMARY_KEYS: dict[str, str] = {
    "customers": "customer_id",
    "accounts": "account_id",
    "credit_cards": "credit_card_id",
    "loans": "loan_id",
    "merchants": "merchant_id",
    "devices": "device_id",
    "sessions": "session_id",
    "behavioral_signals": "signal_id",
    "account_openings": "opening_id",
    "kyc_documents": "kyc_document_id",
    "transactions": "transaction_id",
    "fraud_alerts": "fraud_alert_id",
    "fraud_cases": "fraud_case_id",
    "mule_networks": "mule_network_id",
    "investigations": "investigation_id",
    "approvals": "approval_id",
    "task_history": "task_history_id",
    "agent_feedback": "feedback_id",
    "knowledge_base": "kb_id",
}


def build_primary_index(rows: Iterable[dict], primary_key: str) -> dict[str, dict]:
    return {str(row[primary_key]): row for row in rows if primary_key in row}

