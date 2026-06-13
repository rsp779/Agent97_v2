from __future__ import annotations

from collections.abc import Callable
from typing import Generic, TypeVar

from src.data.data_access_layer import DataAccessLayer


T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, dal: DataAccessLayer, table: str) -> None:
        self.dal = dal
        self.table = table

    def all(self) -> list[dict]:
        return self.dal.load_dataset(self.table)

    def get(self, **criteria) -> dict | None:
        return self.dal.get(self.table, **criteria)

    def get_by_id(self, record_id: str) -> dict | None:
        return self.dal.get_by_id(self.table, record_id)

    def find(self, **criteria) -> list[dict]:
        return self.dal.find(self.table, **criteria)

    def filter(self, predicate: Callable[[dict], bool]) -> list[dict]:
        return self.dal.filter(self.table, predicate)

    def count(self, **criteria) -> int:
        return self.dal.count(self.table, **criteria)

