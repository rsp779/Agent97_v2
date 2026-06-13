from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.data.data_access_layer import DataAccessLayer

from .banking_repository import BankingRepository
from .customer_repository import CustomerRepository
from .digital_repository import DigitalRepository
from .fraud_repository import FraudRepository
from .investigation_repository import InvestigationRepository
from .knowledge_repository import KnowledgeRepository
from .memory_repository import MemoryRepository
from .transaction_repository import TransactionRepository


@dataclass(slots=True)
class RepositoryBundle:
    customer_repository: CustomerRepository
    banking_repository: BankingRepository
    transaction_repository: TransactionRepository
    digital_repository: DigitalRepository
    fraud_repository: FraudRepository
    investigation_repository: InvestigationRepository
    memory_repository: MemoryRepository
    knowledge_repository: KnowledgeRepository


class RepositoryFactory:
    @staticmethod
    def create(data_path: str | Path) -> RepositoryBundle:
        dal = DataAccessLayer.from_path(data_path)
        return RepositoryBundle(
            customer_repository=CustomerRepository(dal),
            banking_repository=BankingRepository(dal),
            transaction_repository=TransactionRepository(dal),
            digital_repository=DigitalRepository(dal),
            fraud_repository=FraudRepository(dal),
            investigation_repository=InvestigationRepository(dal),
            memory_repository=MemoryRepository(dal),
            knowledge_repository=KnowledgeRepository(dal),
        )

