from helix.llm_providers.provider import Provider
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Dict, Any
import os

class OpenAIProvider(Provider):
    """
    OpenAI LLM Provider

    Args:
        api_key (str): The API key for OpenAI.
        model (str): The model to use.
        temperature (float): The temperature to use. (Not supported for gpt-5 models)
        reasoning (Dict[str, Any]): The reasoning to use. (Only supported for gpt-5 models)
    """

    def __init__(
        self,
        api_key: str=None,
        model: str="gpt-5-nano",
        temperature: float | None = None,
        reasoning: Dict[str, Any] | None = None,
        history: bool = False
    ):
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")
            if api_key is None:
                raise ValueError("API key not provided and OPENAI_API_KEY environment variable not set.")

        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.reasoning = reasoning
        self.history = [] if history else None

        self.mcp_enabled = False
        self.mcp_configs = {}

    def enable_mcps(
        self,
        name: str,
        description: str,
        url: str,
    ) -> bool:
        self.mcp_enabled = True
        self.mcp_configs = {
            "type": "mcp",
            "server_label": name,
            "server_description": description,
            "server_url": url,
            "require_approval": "never",
        }
        return True

    def generate(
        self, 
        messages: str | List[Dict[str, Any]], 
        response_model: type[BaseModel] | None = None
    ) -> str | Dict[str, Any]:
        if isinstance(self.history, list):
            if isinstance(messages, list):
                messages = self.history + messages
                self.history = messages
            else:
                messages = self.history + [{"role": "user", "content": messages}]
                self.history = messages
        args = {
            "model": self.model,
            "input": messages
        }
        if self.temperature is not None:
            args["temperature"] = self.temperature
        if self.reasoning is not None:
            args["reasoning"] = self.reasoning
        if self.mcp_enabled:
            args["tools"] = [self.mcp_configs]
        if response_model is not None:
            args["text_format"] = response_model
            response = self.client.responses.parse(**args)
            result = response_model.model_validate(response.output_parsed)
        else:
            response = self.client.responses.create(**args)
            result = response.output_text
        if isinstance(self.history, list):
            self.history.append({"role": "assistant", "content": result})
        return result