from __future__ import annotations

from statistics import mean

from src.models.datasets import Account, CreditCard, Loan

from .base_repository import BaseRepository


class BankingRepository:
    def __init__(self, dal) -> None:
        self.dal = dal

    def get_customer_accounts(self, customer_id: str) -> list[Account]:
        return [Account.model_validate(row) for row in self.dal.find("accounts", customer_id=customer_id)]

    def get_customer_cards(self, customer_id: str) -> list[CreditCard]:
        return [CreditCard.model_validate(row) for row in self.dal.find("credit_cards", customer_id=customer_id)]

    def get_customer_loans(self, customer_id: str) -> list[Loan]:
        return [Loan.model_validate(row) for row in self.dal.find("loans", customer_id=customer_id)]

    def get_total_balance(self, customer_id: str) -> float:
        return round(sum(account.balance for account in self.get_customer_accounts(customer_id)), 2)

    def get_total_credit_limit(self, customer_id: str) -> float:
        return round(sum(card.credit_limit for card in self.get_customer_cards(customer_id)), 2)

    def get_total_exposure(self, customer_id: str) -> float:
        loans = self.get_customer_loans(customer_id)
        return round(self.get_total_balance(customer_id) + self.get_total_credit_limit(customer_id) + sum(loan.principal_amount for loan in loans), 2)

