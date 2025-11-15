from __future__ import annotations

from abc import ABC, abstractmethod

__all__ = [
    "Embeddings",
]


class Embeddings(ABC):
    @abstractmethod
    async def create(self, input: str) -> list[float]:
        """
        Create an embedding for the given input.
        """
