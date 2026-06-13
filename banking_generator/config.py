from dataclasses import dataclass
from pathlib import Path


PRESETS = {
    "small": {
        "customers": 200,
        "accounts": 500,
        "credit_cards": 150,
        "loans": 50,
        "merchants": 30,
        "transactions": 1000,
        "devices": 600,
        "sessions": 1200,
        "behavioral_signals": 1200,
        "account_openings": 500,
        "kyc_documents": 1000,
        "fraud_alerts": 120,
        "fraud_cases": 50,
        "mule_networks": 80,
        "investigations": 100,
        "approvals": 200,
        "task_history": 400,
        "agent_feedback": 150,
        "knowledge_base": 50,
    },
    "medium": {
        "customers": 2000,
        "accounts": 5000,
        "credit_cards": 1500,
        "loans": 500,
        "merchants": 150,
        "transactions": 20000,
        "devices": 6000,
        "sessions": 40000,
        "behavioral_signals": 40000,
        "account_openings": 5000,
        "kyc_documents": 10000,
        "fraud_alerts": 1200,
        "fraud_cases": 500,
        "mule_networks": 800,
        "investigations": 1000,
        "approvals": 2000,
        "task_history": 4000,
        "agent_feedback": 1500,
        "knowledge_base": 200,
    },
    "large": {
        "customers": 10000,
        "accounts": 25000,
        "credit_cards": 7000,
        "loans": 3000,
        "merchants": 500,
        "transactions": 500000,
        "devices": 30000,
        "sessions": 1000000,
        "behavioral_signals": 1000000,
        "account_openings": 50000,
        "kyc_documents": 100000,
        "fraud_alerts": 10000,
        "fraud_cases": 5000,
        "mule_networks": 50000,
        "investigations": 30000,
        "approvals": 50000,
        "task_history": 100000,
        "agent_feedback": 50000,
        "knowledge_base": 1000,
    },
}


@dataclass(frozen=True)
class GeneratorConfig:
    preset: str
    seed: int
    output_dir: Path

    @property
    def counts(self) -> dict[str, int]:
        return PRESETS[self.preset]

