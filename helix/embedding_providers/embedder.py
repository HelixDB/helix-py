from abc import ABC, abstractmethod

class Embedder(ABC):
    @abstractmethod
    async def embed(self, data: str) -> list[float]:
        ...

    @abstractmethod
    async def embed_batch(self, data_list: list[str]) -> list[list[float]]:
        ...