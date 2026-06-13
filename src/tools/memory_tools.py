from __future__ import annotations

from typing import Any

from .base import BaseToolService, ToolSpec
from .schemas import (
    AgentFeedbackInput,
    AgentLearningExamplesInput,
    CustomerInteractionHistoryInput,
    ResolutionHistoryInput,
    TaskHistoryInput,
)
from .schemas import ToolResponse


MEMORY_TOOL_SPECS = (
    ToolSpec("get_agent_feedback", "Return feedback for a task history entry.", AgentFeedbackInput, "get_agent_feedback"),
    ToolSpec("get_task_history", "Return task history context.", TaskHistoryInput, "get_task_history"),
    ToolSpec("get_customer_interaction_history", "Return customer interaction history.", CustomerInteractionHistoryInput, "get_customer_interaction_history"),
    ToolSpec("get_resolution_history", "Return resolution history.", ResolutionHistoryInput, "get_resolution_history"),
    ToolSpec("get_agent_learning_examples", "Return learning examples.", AgentLearningExamplesInput, "get_agent_learning_examples"),
)


class MemoryTools(BaseToolService):
    repository_name = "memory_repository"

    def get_agent_feedback(self, input: AgentFeedbackInput) -> ToolResponse:
        """Return agent feedback for a task history record."""

        return self._execute(
            tool_name="get_agent_feedback",
            repository_used=self.repository_name,
            success_message="agent feedback retrieved",
            action=lambda: [row for row in self.repositories.memory_repository.get_agent_feedback(input.task_history_id)],
        )

    def get_task_history(self, input: TaskHistoryInput) -> ToolResponse:
        """Return task history rows for a task name."""

        return self._execute(
            tool_name="get_task_history",
            repository_used=self.repository_name,
            success_message="task history retrieved",
            action=lambda: [row for row in self.repositories.memory_repository.get_similar_tasks(input.task_name)],
        )

    def get_customer_interaction_history(self, input: CustomerInteractionHistoryInput) -> ToolResponse:
        """Return interaction history associated with a customer identifier."""

        return self._execute(
            tool_name="get_customer_interaction_history",
            repository_used=self.repository_name,
            success_message="customer interaction history retrieved",
            action=lambda: [row for row in self.repositories.memory_repository.get_similar_tasks(input.customer_id)],
        )

    def get_resolution_history(self, input: ResolutionHistoryInput) -> ToolResponse:
        """Return successful task patterns as a resolution proxy."""

        return self._execute(
            tool_name="get_resolution_history",
            repository_used=self.repository_name,
            success_message="resolution history retrieved",
            action=lambda: self.repositories.memory_repository.get_successful_patterns(),
        )

    def get_agent_learning_examples(self, input: AgentLearningExamplesInput) -> ToolResponse:
        """Return compact learning examples for a task name."""

        def action() -> list[dict[str, Any]]:
            rows = self.repositories.memory_repository.get_similar_tasks(input.task_name)
            patterns = self.repositories.memory_repository.get_successful_patterns()
            return [{"task": row, "successful_patterns": patterns.get(input.task_name, 0)} for row in rows]

        return self._execute(
            tool_name="get_agent_learning_examples",
            repository_used=self.repository_name,
            success_message="agent learning examples retrieved",
            action=action,
        )

