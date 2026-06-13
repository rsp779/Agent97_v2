from __future__ import annotations

import json
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from .cache import DatasetCache
from .indexes import PRIMARY_KEYS, build_primary_index
from .query_engine import aggregate as aggregate_rows
from .query_engine import filter_rows, inner_join, matches
from .relationships import RELATIONSHIPS


class StorageBackend(Protocol):
    def load_dataset(self, table: str) -> list[dict[str, Any]]: ...
    def save_dataset(self, table: str, rows: list[dict[str, Any]]) -> None: ...


@dataclass(slots=True)
class JsonDataBackend:
    data_path: Path

    def load_dataset(self, table: str) -> list[dict[str, Any]]:
        path = self.data_path / f"{table}.json"
        if not path.exists():
            return []
        return json.loads(path.read_text(encoding="utf-8"))

    def save_dataset(self, table: str, rows: list[dict[str, Any]]) -> None:
        self.data_path.mkdir(parents=True, exist_ok=True)
        path = self.data_path / f"{table}.json"
        path.write_text(json.dumps(rows, indent=2, sort_keys=True), encoding="utf-8")


class DataAccessLayer:
    def __init__(self, backend: StorageBackend) -> None:
        self.backend = backend
        self.cache: DatasetCache[list[dict[str, Any]]] = DatasetCache()
        self.indexes: dict[str, dict[str, dict[str, Any]]] = {}

    @classmethod
    def from_path(cls, data_path: str | Path) -> "DataAccessLayer":
        return cls(JsonDataBackend(Path(data_path)))

    def load_dataset(self, table: str) -> list[dict[str, Any]]:
        rows = self.cache.get_or_load(table, lambda: self.backend.load_dataset(table))
        self._ensure_index(table, rows)
        return rows

    def _ensure_index(self, table: str, rows: list[dict[str, Any]]) -> None:
        primary_key = PRIMARY_KEYS.get(table)
        if primary_key and table not in self.indexes:
            self.indexes[table] = build_primary_index(rows, primary_key)

    def get(self, table: str, **criteria: Any) -> dict[str, Any] | None:
        rows = self.load_dataset(table)
        if not criteria:
            return rows[0] if rows else None
        if len(criteria) == 1:
            key, value = next(iter(criteria.items()))
            primary_key = PRIMARY_KEYS.get(table)
            if primary_key == key:
                return self.indexes.get(table, {}).get(str(value))
        matches_ = [row for row in rows if matches(row, criteria)]
        return matches_[0] if matches_ else None

    def get_by_id(self, table: str, record_id: str) -> dict[str, Any] | None:
        primary_key = PRIMARY_KEYS.get(table)
        if primary_key is None:
            return self.get(table, **{f"id": record_id})
        self.load_dataset(table)
        return self.indexes.get(table, {}).get(str(record_id))

    def find(self, table: str, **criteria: Any) -> list[dict[str, Any]]:
        return filter_rows(self.load_dataset(table), criteria)

    def filter(self, table: str, predicate: Callable[[dict[str, Any]], bool]) -> list[dict[str, Any]]:
        return [row for row in self.load_dataset(table) if predicate(row)]

    def exists(self, table: str, **criteria: Any) -> bool:
        return self.get(table, **criteria) is not None

    def count(self, table: str, **criteria: Any) -> int:
        return len(self.find(table, **criteria)) if criteria else len(self.load_dataset(table))

    def children(self, parent_table: str, parent_id: str) -> dict[str, list[dict[str, Any]]]:
        related: dict[str, list[dict[str, Any]]] = {}
        for child_table, rules in RELATIONSHIPS.items():
            matches_: list[dict[str, Any]] = []
            for fk_field, rule_parent, parent_field in rules:
                if rule_parent != parent_table:
                    continue
                matches_.extend(self.find(child_table, **{fk_field: parent_id}))
            if matches_:
                related[child_table] = matches_
        return related

    def parent(self, child_table: str, child_id: str, fk_field: str, parent_table: str) -> dict[str, Any] | None:
        child = self.get_by_id(child_table, child_id)
        if not child:
            return None
        return self.get_by_id(parent_table, str(child.get(fk_field, "")))

    def join(self, left_table: str, right_table: str, left_key: str, right_key: str) -> list[dict[str, Any]]:
        right_rows = self.load_dataset(right_table)
        right_index = {str(row[right_key]): row for row in right_rows if right_key in row}
        return inner_join(self.load_dataset(left_table), right_index, left_key, right_key)

    def aggregate(self, table: str, group_by: str | None = None, metric: Callable[[list[dict[str, Any]]], Any] | None = None) -> Any:
        return aggregate_rows(self.load_dataset(table), group_by=group_by, metric=metric)

    def save_dataset(self, table: str, rows: list[dict[str, Any]]) -> None:
        self.backend.save_dataset(table, rows)
        self.cache.set(table, rows)
        self.indexes.pop(table, None)
        self._ensure_index(table, rows)

