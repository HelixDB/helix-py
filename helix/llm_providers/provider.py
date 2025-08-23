from abc import ABC, abstractmethod

class Provider(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        ...
