from __future__ import annotations

from collections import Counter


class MemoryRepository:
    def __init__(self, dal) -> None:
        self.dal = dal

    def get_similar_tasks(self, task_name: str) -> list[dict]:
        return self.dal.find("task_history", task_name=task_name)

    def get_successful_patterns(self) -> dict[str, int]:
        rows = [row for row in self.dal.load_dataset("task_history") if row.get("task_status") == "done"]
        return dict(Counter(row["task_name"] for row in rows))

    def get_agent_feedback(self, task_history_id: str) -> list[dict]:
        return self.dal.find("agent_feedback", task_history_id=task_history_id)

    def store_task_outcome(self, outcome: dict) -> dict:
        rows = self.dal.load_dataset("task_history")
        rows.append(outcome)
        self.dal.save_dataset("task_history", rows)
        return outcome

