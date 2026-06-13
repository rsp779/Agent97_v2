from __future__ import annotations

from src.models.datasets import Approval, Investigation


class InvestigationRepository:
    def __init__(self, dal) -> None:
        self.dal = dal

    def get_investigation(self, investigation_id: str) -> Investigation | None:
        row = self.dal.get_by_id("investigations", investigation_id)
        return Investigation.model_validate(row) if row else None

    def get_customer_investigations(self, customer_id: str) -> list[Investigation]:
        cases = {case["fraud_case_id"] for case in self.dal.find("fraud_cases", customer_id=customer_id)}
        return [Investigation.model_validate(row) for row in self.dal.load_dataset("investigations") if row["fraud_case_id"] in cases]

    def get_pending_approvals(self, customer_id: str) -> list[Approval]:
        investigation_ids = {row.investigation_id for row in self.get_customer_investigations(customer_id)}
        return [Approval.model_validate(row) for row in self.dal.load_dataset("approvals") if row["investigation_id"] in investigation_ids and row["decision"] == "request_more_info"]

    def get_approval_history(self, investigation_id: str) -> list[Approval]:
        return [Approval.model_validate(row) for row in self.dal.find("approvals", investigation_id=investigation_id)]

