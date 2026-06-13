from __future__ import annotations

from typing import Any

from .base import BaseToolService, ToolSpec
from .schemas import (
    AccountBalanceInput,
    AccountSummaryInput,
    BankingOverviewInput,
    CreditCardSummaryInput,
    CreditUtilizationInput,
    CustomerAccountsInput,
    CustomerExposureInput,
    LoanSummaryInput,
)
from .schemas import ToolResponse


BANKING_TOOL_SPECS = (
    ToolSpec("get_customer_accounts", "Return accounts for a customer.", CustomerAccountsInput, "get_customer_accounts"),
    ToolSpec("get_account_summary", "Return an account summary.", AccountSummaryInput, "get_account_summary"),
    ToolSpec("get_account_balance", "Return an account or customer balance.", AccountBalanceInput, "get_account_balance"),
    ToolSpec("get_credit_utilization", "Return a customer credit utilization summary.", CreditUtilizationInput, "get_credit_utilization"),
    ToolSpec("get_customer_exposure", "Return total customer exposure.", CustomerExposureInput, "get_customer_exposure"),
    ToolSpec("get_loan_summary", "Return customer loan summary.", LoanSummaryInput, "get_loan_summary"),
    ToolSpec("get_credit_card_summary", "Return customer credit card summary.", CreditCardSummaryInput, "get_credit_card_summary"),
    ToolSpec("get_banking_overview", "Return a banking overview.", BankingOverviewInput, "get_banking_overview"),
)


class BankingTools(BaseToolService):
    repository_name = "banking_repository"

    def _find_account(self, account_id: str) -> dict[str, Any] | None:
        for customer in self.repositories.customer_repository.get_customers():
            for account in self.repositories.banking_repository.get_customer_accounts(customer.customer_id):
                if account.account_id == account_id:
                    return account.model_dump()
        return None

    def get_customer_accounts(self, input: CustomerAccountsInput) -> ToolResponse:
        """Return all accounts for a customer."""

        return self._execute(
            tool_name="get_customer_accounts",
            repository_used=self.repository_name,
            success_message="customer accounts retrieved",
            action=lambda: [account.model_dump() for account in self.repositories.banking_repository.get_customer_accounts(input.customer_id)],
        )

    def get_account_summary(self, input: AccountSummaryInput) -> ToolResponse:
        """Return an account summary for a customer or single account."""

        def action() -> dict[str, Any]:
            if input.account_id:
                account = self._find_account(input.account_id)
                return account or {}
            if input.customer_id:
                accounts = self.repositories.banking_repository.get_customer_accounts(input.customer_id)
                return {
                    "customer_id": input.customer_id,
                    "count": len(accounts),
                    "total_balance": round(sum(account.balance for account in accounts), 2),
                    "accounts": [account.model_dump() for account in accounts],
                }
            return {}

        return self._execute(
            tool_name="get_account_summary",
            repository_used=self.repository_name,
            success_message="account summary retrieved",
            action=action,
        )

    def get_account_balance(self, input: AccountBalanceInput) -> ToolResponse:
        """Return the balance for a single account or customer."""

        def action() -> dict[str, Any]:
            if input.account_id:
                account = self._find_account(input.account_id)
                return {"account_id": input.account_id, "balance": account["balance"]} if account else {}
            if input.customer_id:
                return {
                    "customer_id": input.customer_id,
                    "balance": self.repositories.banking_repository.get_total_balance(input.customer_id),
                }
            return {}

        return self._execute(
            tool_name="get_account_balance",
            repository_used=self.repository_name,
            success_message="account balance retrieved",
            action=action,
        )

    def get_credit_utilization(self, input: CreditUtilizationInput) -> ToolResponse:
        """Return a basic credit utilization view."""

        def action() -> dict[str, Any]:
            cards = self.repositories.banking_repository.get_customer_cards(input.customer_id)
            limit = round(sum(card.credit_limit for card in cards), 2)
            exposure = self.repositories.banking_repository.get_total_exposure(input.customer_id)
            utilization = round(exposure / limit, 4) if limit else 0.0
            return {"customer_id": input.customer_id, "credit_limit": limit, "exposure": exposure, "utilization": utilization}

        return self._execute(
            tool_name="get_credit_utilization",
            repository_used=self.repository_name,
            success_message="credit utilization retrieved",
            action=action,
        )

    def get_customer_exposure(self, input: CustomerExposureInput) -> ToolResponse:
        """Return total exposure for a customer."""

        return self._execute(
            tool_name="get_customer_exposure",
            repository_used=self.repository_name,
            success_message="customer exposure retrieved",
            action=lambda: {"customer_id": input.customer_id, "exposure": self.repositories.banking_repository.get_total_exposure(input.customer_id)},
        )

    def get_loan_summary(self, input: LoanSummaryInput) -> ToolResponse:
        """Return a loan summary for a customer."""

        def action() -> dict[str, Any]:
            loans = self.repositories.banking_repository.get_customer_loans(input.customer_id)
            return {
                "customer_id": input.customer_id,
                "count": len(loans),
                "principal_amount": round(sum(loan.principal_amount for loan in loans), 2),
                "loans": [loan.model_dump() for loan in loans],
            }

        return self._execute(
            tool_name="get_loan_summary",
            repository_used=self.repository_name,
            success_message="loan summary retrieved",
            action=action,
        )

    def get_credit_card_summary(self, input: CreditCardSummaryInput) -> ToolResponse:
        """Return a credit card summary for a customer."""

        def action() -> dict[str, Any]:
            cards = self.repositories.banking_repository.get_customer_cards(input.customer_id)
            return {
                "customer_id": input.customer_id,
                "count": len(cards),
                "credit_limit": round(sum(card.credit_limit for card in cards), 2),
                "cards": [card.model_dump() for card in cards],
            }

        return self._execute(
            tool_name="get_credit_card_summary",
            repository_used=self.repository_name,
            success_message="credit card summary retrieved",
            action=action,
        )

    def get_banking_overview(self, input: BankingOverviewInput) -> ToolResponse:
        """Return a banking overview for a customer."""

        def action() -> dict[str, Any]:
            accounts = self.repositories.banking_repository.get_customer_accounts(input.customer_id)
            cards = self.repositories.banking_repository.get_customer_cards(input.customer_id)
            loans = self.repositories.banking_repository.get_customer_loans(input.customer_id)
            return {
                "customer_id": input.customer_id,
                "accounts": len(accounts),
                "cards": len(cards),
                "loans": len(loans),
                "total_balance": round(sum(account.balance for account in accounts), 2),
                "total_credit_limit": round(sum(card.credit_limit for card in cards), 2),
                "total_exposure": self.repositories.banking_repository.get_total_exposure(input.customer_id),
            }

        return self._execute(
            tool_name="get_banking_overview",
            repository_used=self.repository_name,
            success_message="banking overview retrieved",
            action=action,
        )

