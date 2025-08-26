from helix.providers.provider import Provider
from google import genai
from google.genai import types
from fastmcp import Client
from pydantic import BaseModel
from enum import Enum
from typing import List, Any
from dotenv import load_dotenv
import json
import os
import asyncio

DEFAULT_MODEL = "gemini-2.0-flash"
DEFAULT_MCP_URL = "http://localhost:8000/mcp/"

class Part(BaseModel):
    text: Any | None = None

class Role(Enum):
    user = "user"
    model = "model"

class Message(BaseModel):
    role: Role
    parts: List[Part]

class GeminiProvider(Provider):
    """
    Gemini LLM Provider

    Args:
        api_key (str, optional): The API key to use. (Defaults to None)
        model (str, optional): The model to use. (Defaults to "gemini-2.0-flash")
        temperature (float, optional): The temperature setting to use. (Defaults to None)
        thinking_budget (float, optional): The thinking budget to use. (Defaults to 0)
        history (bool, optional): Whether to use history. (Defaults to False)
    """
    def __init__(
        self,
        api_key: str=None,
        model: str = DEFAULT_MODEL,
        temperature: float | None = None,
        thinking_budget: float = 0,
        history: bool = False,
    ):
        if api_key is None:
            load_dotenv()
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key is None:
                raise ValueError("API key not provided and GEMINI_API_KEY environment variable not set.")
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.thinking_budget = thinking_budget
        self.history = [] if history else None
        self.mcp_enabled = False
        self.mcp_client = None
        self._loop = asyncio.new_event_loop()

    def enable_mcps(
        self,
        name: str,
        url: str = DEFAULT_MCP_URL,
    ) -> bool:
        """
        Enable MCPs for the Gemini provider.

        Args:
            name (str): The name of the server.
            url (str, optional): The URL of the server. (Defaults to "http://localhost:8000/mcp/")

        Returns:
            bool: True if MCPs are enabled, False otherwise.
        """
        self.mcp_client = Client(url)
        self.mcp_enabled = True
        return True

    def generate(
        self,
        messages: str | List[Message] | List[dict],
        response_model: BaseModel | None = None
    ) -> str | BaseModel:
        """
        Generate a response from the Gemini provider.

        Args:
            messages (str | List[Message] | List[dict]): The messages to send to the provider.
            response_model (BaseModel | None, optional): The response model to use. (Defaults to None)

        Returns:
            str | BaseModel: The response from the provider.
        """
        if isinstance(messages, list) and all(isinstance(msg, Message) for msg in messages):
            if isinstance(self.history, list):
                messages = self.history + [msg.model_dump(mode="json") for msg in messages]
                self.history = messages
            else:
                messages = [msg.model_dump(mode="json") for msg in messages]
        elif isinstance(messages, str):
            if isinstance(self.history, list):
                messages = self.history + [Message(role=Role.user, parts=[Part(text=messages)]).model_dump(mode="json")]
                self.history = messages
            else:
                messages = [Message(role=Role.user, parts=[Part(text=messages)]).model_dump(mode="json")]
        elif isinstance(messages, list) and all(isinstance(msg, dict) for msg in messages):
            try:
                validated = [Message.model_validate(msg).model_dump(mode="json") for msg in messages]
                if isinstance(self.history, list):
                    messages = self.history + validated
                    self.history = messages
                else:
                    messages = validated
            except Exception as e:
                raise ValueError("Invalid message type")
        else:
            raise ValueError("Invalid message type")
        args = {
            "model": self.model,
            "contents": messages
        }
        config_args = {}
        if self.temperature is not None:
            config_args["temperature"] = self.temperature
        config_args["thinking_config"] = types.ThinkingConfig(thinking_budget=self.thinking_budget)
        if response_model is not None:
            config_args["response_mime_type"] = "application/json"
            config_args["response_schema"] = response_model
        if self.mcp_enabled:
            async def gen():
                async with self.mcp_client:
                    config_args["tools"] = [self.mcp_client.session]
                    config = types.GenerateContentConfig(**config_args)
                    args["config"] = config
                    response = await self.client.aio.models.generate_content(**args)
                return response
            response = self._loop.run_until_complete(gen())
        else:
            config = types.GenerateContentConfig(**config_args)
            args["config"] = config
            response = self.client.models.generate_content(**args)
        if response_model is not None:
            result = response_model.model_validate(response.parsed)
        else:
            result = response.text
        if isinstance(self.history, list):
            text = json.dumps(result.model_dump(mode="json")) if isinstance(result, BaseModel) else str(result)
            self.history.append(Message(role=Role.model, parts=[Part(text=text)]).model_dump(mode="json"))
        return result