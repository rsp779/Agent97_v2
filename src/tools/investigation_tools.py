from __future__ import annotations

from typing import Any

from .base import BaseToolService, ToolSpec
from .schemas import (
    ApprovalHistoryInput,
    CaseDetailsInput,
    CaseParticipantsInput,
    CaseTimelineInput,
    InvestigationStatusInput,
    InvestigationSummaryInput,
    OpenTasksInput,
    RelatedCasesInput,
)
from .schemas import ToolResponse


INVESTIGATION_TOOL_SPECS = (
    ToolSpec("get_case_details", "Return investigation case details.", CaseDetailsInput, "get_case_details"),
    ToolSpec("get_case_timeline", "Return investigation case timeline.", CaseTimelineInput, "get_case_timeline"),
    ToolSpec("get_approval_history", "Return approval history.", ApprovalHistoryInput, "get_approval_history"),
    ToolSpec("get_open_tasks", "Return open investigation tasks.", OpenTasksInput, "get_open_tasks"),
    ToolSpec("get_investigation_summary", "Return an investigation summary.", InvestigationSummaryInput, "get_investigation_summary"),
    ToolSpec("get_investigation_status", "Return investigation status.", InvestigationStatusInput, "get_investigation_status"),
    ToolSpec("get_related_cases", "Return related cases.", RelatedCasesInput, "get_related_cases"),
    ToolSpec("get_case_participants", "Return case participants.", CaseParticipantsInput, "get_case_participants"),
)


class InvestigationTools(BaseToolService):
    repository_name = "investigation_repository"

    def get_case_details(self, input: CaseDetailsInput) -> ToolResponse:
        """Return a single investigation detail record."""

        return self._execute(
            tool_name="get_case_details",
            repository_used=self.repository_name,
            success_message="case details retrieved",
            action=lambda: self.repositories.investigation_repository.get_investigation(input.investigation_id).model_dump() if self.repositories.investigation_repository.get_investigation(input.investigation_id) else {},
        )

    def get_case_timeline(self, input: CaseTimelineInput) -> ToolResponse:
        """Return an investigation timeline from approvals and linked case data."""

        def action() -> list[dict[str, Any]]:
            investigation = self.repositories.investigation_repository.get_investigation(input.investigation_id)
            if investigation is None:
                return []
            approvals = self.repositories.investigation_repository.get_approval_history(input.investigation_id)
            events = [{"type": "investigation", "id": investigation.investigation_id, "status": investigation.status, "ts": investigation.started_at}]
            events.extend({"type": "approval", "id": approval.approval_id, "decision": approval.decision, "ts": approval.approved_at} for approval in approvals)
            events.sort(key=lambda row: str(row.get("ts", "")))
            return events

        return self._execute(
            tool_name="get_case_timeline",
            repository_used=self.repository_name,
            success_message="case timeline retrieved",
            action=action,
        )

    def get_approval_history(self, input: ApprovalHistoryInput) -> ToolResponse:
        """Return approval history for an investigation."""

        return self._execute(
            tool_name="get_approval_history",
            repository_used=self.repository_name,
            success_message="approval history retrieved",
            action=lambda: [approval.model_dump() for approval in self.repositories.investigation_repository.get_approval_history(input.investigation_id)],
        )

    def get_open_tasks(self, input: OpenTasksInput) -> ToolResponse:
        """Return open tasks inferred from approvals and investigation state."""

        def action() -> list[dict[str, Any]]:
            if input.investigation_id:
                approvals = self.repositories.investigation_repository.get_approval_history(input.investigation_id)
                return [approval.model_dump() for approval in approvals if approval.decision == "request_more_info"]
            if input.customer_id:
                pending = self.repositories.investigation_repository.get_pending_approvals(input.customer_id)
                return [approval.model_dump() for approval in pending]
            return []

        return self._execute(
            tool_name="get_open_tasks",
            repository_used=self.repository_name,
            success_message="open tasks retrieved",
            action=action,
        )

    def get_investigation_summary(self, input: InvestigationSummaryInput) -> ToolResponse:
        """Return a summary for an investigation or customer."""

        def action() -> dict[str, Any]:
            if input.investigation_id:
                investigation = self.repositories.investigation_repository.get_investigation(input.investigation_id)
                if investigation is None:
                    return {}
                approvals = self.repositories.investigation_repository.get_approval_history(input.investigation_id)
                return {
                    "investigation": investigation.model_dump(),
                    "approvals": len(approvals),
                    "status": investigation.status,
                }
            if input.customer_id:
                investigations = self.repositories.investigation_repository.get_customer_investigations(input.customer_id)
                return {
                    "customer_id": input.customer_id,
                    "count": len(investigations),
                    "open": sum(1 for item in investigations if item.status == "open"),
                    "closed": sum(1 for item in investigations if item.status == "closed"),
                }
            return {}

        return self._execute(
            tool_name="get_investigation_summary",
            repository_used=self.repository_name,
            success_message="investigation summary retrieved",
            action=action,
        )

    def get_investigation_status(self, input: InvestigationStatusInput) -> ToolResponse:
        """Return the current investigation status."""

        return self._execute(
            tool_name="get_investigation_status",
            repository_used=self.repository_name,
            success_message="investigation status retrieved",
            action=lambda: self.repositories.investigation_repository.get_investigation(input.investigation_id).model_dump() if self.repositories.investigation_repository.get_investigation(input.investigation_id) else {},
        )

    def get_related_cases(self, input: RelatedCasesInput) -> ToolResponse:
        """Return related cases for a customer."""

        return self._execute(
            tool_name="get_related_cases",
            repository_used=self.repository_name,
            success_message="related cases retrieved",
            action=lambda: [case.model_dump() for case in self.repositories.investigation_repository.get_customer_investigations(input.customer_id)],
        )

    def get_case_participants(self, input: CaseParticipantsInput) -> ToolResponse:
        """Return a compact case participant summary."""

        def action() -> dict[str, Any]:
            investigation = self.repositories.investigation_repository.get_investigation(input.investigation_id)
            if investigation is None:
                return {}
            approvals = self.repositories.investigation_repository.get_approval_history(input.investigation_id)
            return {
                "investigation_id": input.investigation_id,
                "assigned_team": investigation.assigned_team,
                "approvers": [approval.approver_role for approval in approvals],
                "customer_id": input.customer_id,
            }

        return self._execute(
            tool_name="get_case_participants",
            repository_used=self.repository_name,
            success_message="case participants retrieved",
            action=action,
        )
