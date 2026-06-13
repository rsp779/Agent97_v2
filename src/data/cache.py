from __future__ import annotations

from collections.abc import Callable
from typing import Generic, TypeVar


T = TypeVar("T")


class DatasetCache(Generic[T]):
    def __init__(self) -> None:
        self._datasets: dict[str, T] = {}

    def get_or_load(self, name: str, loader: Callable[[], T]) -> T:
        if name not in self._datasets:
            self._datasets[name] = loader()
        return self._datasets[name]

    def get(self, name: str) -> T | None:
        return self._datasets.get(name)

    def set(self, name: str, value: T) -> None:
        self._datasets[name] = value

    def keys(self) -> list[str]:
        return sorted(self._datasets)

