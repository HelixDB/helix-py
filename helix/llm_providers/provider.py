from abc import ABC, abstractmethod

class Provider(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        ...
