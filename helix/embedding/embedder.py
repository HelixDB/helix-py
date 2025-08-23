from abc import ABC, abstractmethod

class Embedder(ABC):
    @abstractmethod
    def embed(self, data: str) -> list[float]:
        ...

    @abstractmethod
    def embed_batch(self, data_list: list[str]) -> list[list[float]]:
        ...