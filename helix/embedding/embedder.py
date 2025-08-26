from abc import ABC, abstractmethod
from typing import List

class Embedder(ABC):
    @abstractmethod
    def embed(self, data: str) -> List[float]:
        ...

    @abstractmethod
    def embed_batch(self, data_list: List[str]) -> List[List[float]]:
        ...