from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import List

class Message(BaseModel, ABC):
    pass

class Provider(ABC):
    @abstractmethod
    def enable_mcps(
        self,
        name: str,
        url: str,
    ) -> bool:
        ...

    @abstractmethod
    def generate(
        self, 
        messages: str | List[Message] | List[dict],
        response_model: BaseModel | None = None
    ) -> str | BaseModel:
        ...