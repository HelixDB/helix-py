from helix.llm_providers.provider import Provider
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Dict, Any
from dotenv import load_dotenv
import os

DEFAULT_MODEL = "gpt-5-nano"
DEFAULT_MCP_URL = "http://localhost:8000/mcp/"

class OpenAIProvider(Provider):
    """
    OpenAI LLM Provider

    Args:
        api_key (str): The API key for OpenAI. (Defaults to OPENAI_API_KEY environment variable)
        model (str): The model to use.
        temperature (float): The temperature setting to use. (Not supported for gpt-5 models)
        reasoning (Dict[str, Any]): The reasoning setting to use. (Only supported for gpt-5 models)
    """

    def __init__(
        self,
        api_key: str=None,
        model: str=DEFAULT_MODEL,
        temperature: float | None = None,
        reasoning: Dict[str, Any] | None = None,
        history: bool = False,
        base_url: str | None = None,
    ):
        if api_key is None:
            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key is None:
                raise ValueError("API key not provided and OPENAI_API_KEY environment variable not set.")

        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.temperature = temperature
        self.reasoning = reasoning
        self.history = [] if history else None
        self.mcp_configs = None

    def enable_mcps(
        self,
        name: str,
        description: str,
        url: str = DEFAULT_MCP_URL,
    ) -> bool:
        """
        Enable MCPs for the OpenAI provider.

        Args:
            name (str): The name of the server.
            description (str): The description of the server.
            url (str, optional): The URL of the server. (Defaults to "http://localhost:8000/mcp/")

        Returns:
            bool: True if MCPs are enabled, False otherwise.
        """
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
        response_model: BaseModel | None = None
    ) -> str | BaseModel:
        """
        Generate a response from the OpenAI provider.

        Args:
            messages (str | List[Dict[str, Any]]): The messages to send to the provider.
            response_model (BaseModel | None, optional): The response model to use. (Defaults to None)

        Returns:
            str | BaseModel: The response from the provider.
        """
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
        if self.mcp_configs is not None:
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