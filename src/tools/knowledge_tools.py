from __future__ import annotations

from typing import Any

from .base import BaseToolService, ToolSpec
from .schemas import (
    FraudProcedureInput,
    InvestigationPlaybookInput,
    KycGuidanceInput,
    KnowledgeArticleInput,
    KnowledgeSearchInput,
    OperationalGuidanceInput,
)
from .schemas import ToolResponse


KNOWLEDGE_TOOL_SPECS = (
    ToolSpec("search_knowledge", "Search knowledge articles.", KnowledgeSearchInput, "search_knowledge"),
    ToolSpec("get_knowledge_article", "Return a knowledge article.", KnowledgeArticleInput, "get_knowledge_article"),
    ToolSpec("retrieve_operational_guidance", "Return operational guidance.", OperationalGuidanceInput, "retrieve_operational_guidance"),
    ToolSpec("retrieve_investigation_playbook", "Return the investigation playbook.", InvestigationPlaybookInput, "retrieve_investigation_playbook"),
    ToolSpec("retrieve_fraud_procedure", "Return fraud procedure guidance.", FraudProcedureInput, "retrieve_fraud_procedure"),
    ToolSpec("retrieve_kyc_guidance", "Return KYC guidance.", KycGuidanceInput, "retrieve_kyc_guidance"),
)


class KnowledgeTools(BaseToolService):
    repository_name = "knowledge_repository"

    def search_knowledge(self, input: KnowledgeSearchInput) -> ToolResponse:
        """Search the knowledge base by query."""

        return self._execute(
            tool_name="search_knowledge",
            repository_used=self.repository_name,
            success_message="knowledge search completed",
            action=lambda: [row for row in self.repositories.knowledge_repository.search_documents(input.query)],
        )

    def get_knowledge_article(self, input: KnowledgeArticleInput) -> ToolResponse:
        """Return a single knowledge article if found."""

        def action() -> dict[str, Any]:
            rows = self.repositories.knowledge_repository.search_documents(input.kb_id)
            for row in rows:
                if row.get("kb_id") == input.kb_id:
                    return row
            return {}

        return self._execute(
            tool_name="get_knowledge_article",
            repository_used=self.repository_name,
            success_message="knowledge article retrieved",
            action=action,
        )

    def retrieve_operational_guidance(self, input: OperationalGuidanceInput) -> ToolResponse:
        """Return operational guidance articles."""

        return self._execute(
            tool_name="retrieve_operational_guidance",
            repository_used=self.repository_name,
            success_message="operational guidance retrieved",
            action=lambda: [row for row in self.repositories.knowledge_repository.search_policy(input.query or "ops")],
        )

    def retrieve_investigation_playbook(self, input: InvestigationPlaybookInput) -> ToolResponse:
        """Return investigation playbook content."""

        return self._execute(
            tool_name="retrieve_investigation_playbook",
            repository_used=self.repository_name,
            success_message="investigation playbook retrieved",
            action=lambda: [row for row in self.repositories.knowledge_repository.search_policy(input.query or "investigation")],
        )

    def retrieve_fraud_procedure(self, input: FraudProcedureInput) -> ToolResponse:
        """Return fraud procedure content."""

        return self._execute(
            tool_name="retrieve_fraud_procedure",
            repository_used=self.repository_name,
            success_message="fraud procedure retrieved",
            action=lambda: [row for row in self.repositories.knowledge_repository.search_policy(input.query or "fraud")],
        )

    def retrieve_kyc_guidance(self, input: KycGuidanceInput) -> ToolResponse:
        """Return KYC guidance content."""

        return self._execute(
            tool_name="retrieve_kyc_guidance",
            repository_used=self.repository_name,
            success_message="kyc guidance retrieved",
            action=lambda: [row for row in self.repositories.knowledge_repository.search_policy(input.query or "kyc")],
        )

