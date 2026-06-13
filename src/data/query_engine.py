from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any


def matches(row: dict, criteria: dict[str, Any]) -> bool:
    return all(row.get(key) == value for key, value in criteria.items())


def filter_rows(rows: Iterable[dict], criteria: dict[str, Any]) -> list[dict]:
    return [row for row in rows if matches(row, criteria)]


def inner_join(left: Iterable[dict], right_index: dict[str, dict], left_key: str, right_key: str, suffix: str = "_right") -> list[dict]:
    joined: list[dict] = []
    for row in left:
        key = row.get(left_key)
        if key in right_index:
            other = right_index[key]
            merged = dict(row)
            for field, value in other.items():
                if field == right_key:
                    continue
                if field in merged and merged[field] != value:
                    merged[f"{field}{suffix}"] = value
                else:
                    merged[field] = value
            joined.append(merged)
    return joined


def aggregate(rows: Iterable[dict], group_by: str | None = None, metric: Callable[[list[dict]], Any] | None = None) -> Any:
    data = list(rows)
    if group_by is None:
        return metric(data) if metric else data
    grouped: dict[Any, list[dict]] = {}
    for row in data:
        grouped.setdefault(row.get(group_by), []).append(row)
    if metric:
        return {key: metric(items) for key, items in grouped.items()}
    return grouped

