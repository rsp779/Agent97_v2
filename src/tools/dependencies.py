from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.repositories.factory import RepositoryBundle, RepositoryFactory

from .banking_tools import BankingTools
from .customer_tools import CustomerTools
from .digital_tools import DigitalTools
from .fraud_tools import FraudTools
from .investigation_tools import InvestigationTools
from .knowledge_tools import KnowledgeTools
from .memory_tools import MemoryTools
from .transaction_tools import TransactionTools


def load_repositories(data_path: str | Path) -> RepositoryBundle:
    return RepositoryFactory.create(data_path)


def _repositories(repositories: RepositoryBundle | None, data_path: str | Path | None) -> RepositoryBundle:
    if repositories is not None:
        return repositories
    return load_repositories(data_path or "output/small")


def get_customer_tools(repositories: RepositoryBundle | None = None, data_path: str | Path | None = None) -> CustomerTools:
    return CustomerTools(_repositories(repositories, data_path))


def get_banking_tools(repositories: RepositoryBundle | None = None, data_path: str | Path | None = None) -> BankingTools:
    return BankingTools(_repositories(repositories, data_path))


def get_transaction_tools(repositories: RepositoryBundle | None = None, data_path: str | Path | None = None) -> TransactionTools:
    return TransactionTools(_repositories(repositories, data_path))


def get_digital_tools(repositories: RepositoryBundle | None = None, data_path: str | Path | None = None) -> DigitalTools:
    return DigitalTools(_repositories(repositories, data_path))


def get_fraud_tools(repositories: RepositoryBundle | None = None, data_path: str | Path | None = None) -> FraudTools:
    return FraudTools(_repositories(repositories, data_path))


def get_investigation_tools(repositories: RepositoryBundle | None = None, data_path: str | Path | None = None) -> InvestigationTools:
    return InvestigationTools(_repositories(repositories, data_path))


def get_memory_tools(repositories: RepositoryBundle | None = None, data_path: str | Path | None = None) -> MemoryTools:
    return MemoryTools(_repositories(repositories, data_path))


def get_knowledge_tools(repositories: RepositoryBundle | None = None, data_path: str | Path | None = None) -> KnowledgeTools:
    return KnowledgeTools(_repositories(repositories, data_path))


@dataclass(slots=True)
class ToolServiceBundle:
    customer_tools: CustomerTools
    banking_tools: BankingTools
    transaction_tools: TransactionTools
    digital_tools: DigitalTools
    fraud_tools: FraudTools
    investigation_tools: InvestigationTools
    memory_tools: MemoryTools
    knowledge_tools: KnowledgeTools


def get_tool_services(repositories: RepositoryBundle | None = None, data_path: str | Path | None = None) -> ToolServiceBundle:
    bundle = _repositories(repositories, data_path)
    return ToolServiceBundle(
        customer_tools=CustomerTools(bundle),
        banking_tools=BankingTools(bundle),
        transaction_tools=TransactionTools(bundle),
        digital_tools=DigitalTools(bundle),
        fraud_tools=FraudTools(bundle),
        investigation_tools=InvestigationTools(bundle),
        memory_tools=MemoryTools(bundle),
        knowledge_tools=KnowledgeTools(bundle),
    )

