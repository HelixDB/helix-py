from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import List, Dict, Any

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
        messages: str | List[Dict[str, Any]],
        response_model: type[BaseModel] | None = None
    ) -> str | Dict[str, Any]:
        ...