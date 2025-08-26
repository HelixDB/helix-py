from helix.providers.provider import Provider
import anthropic
from pydantic import BaseModel
from enum import Enum
from typing import List, Any
from dotenv import load_dotenv
import json
import os

DEFAULT_MODEL = "claude-3-5-haiku-20241022"
DEFAULT_MAX_TOKENS = 3200

class Role(Enum):
    user = "user"
    model = "assistant"

class Message(BaseModel):
    role: Role
    content: Any

class AnthropicProvider(Provider):
    """
    Anthropic LLM Provider

    Args:
        api_key (str, optional): The API key to use. (Defaults to None)
        model (str, optional): The model to use. (Defaults to "claude-3-5-haiku-20241022")
        temperature (float, optional): The temperature setting to use. (Defaults to None)
        thinking (float, optional): The thinking budget to use. (Defaults to 0)
        max_tokens (int, optional): The maximum number of tokens to use. (Defaults to 3200)
        history (bool, optional): Whether to use history. (Defaults to False)
    """
    def __init__(
        self,
        api_key: str=None,
        model: str = DEFAULT_MODEL,
        temperature: float | None = None,
        thinking: float = 0,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        history: bool = False,
    ):
        if api_key is None:
            load_dotenv()
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key is None:
                raise ValueError("API key not provided and ANTHROPIC_API_KEY environment variable not set.")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.temperature = temperature
        if thinking > 0:
            self.thinking = {"type": "enabled", "budget_tokens": thinking}
        else:
            self.thinking = {"type": "disabled"}
        self.max_tokens = max_tokens
        self.history = [] if history else None
        self.mcp_config = None

    def enable_mcps(
        self,
        name: str,
        url: str,
    ) -> bool:
        """
        Enable MCPs for the Anthropic provider.

        Note: Local MCP servers are not supported by Anthropic.

        Args:
            name (str): The name of the server.
            url (str, optional): The URL of the server. (Defaults to "http://localhost:8000/mcp/")

        Returns:
            bool: True if MCPs are enabled, False otherwise.
        """
        self.mcp_config = {"type": "url", "url": url, "name": name}
        return True

    def generate(
        self, 
        messages: str | List[Message] | List[dict], 
        response_model: BaseModel | None = None,
    ) -> str | BaseModel:
        """
        Generate a response from the LLM.

        Args:
            messages (str | List[Message] | List[dict]): The messages to send to the LLM.
            response_model (BaseModel | None, optional): The response model to use. (Defaults to None)

        Returns:
            str | BaseModel: The response from the LLM.
        """
        if isinstance(messages, list) and all(isinstance(msg, Message) for msg in messages):
            if isinstance(self.history, list):
                messages = self.history + [msg.model_dump(mode="json") for msg in messages]
                self.history = messages
            else:
                messages = [msg.model_dump(mode="json") for msg in messages]
        elif isinstance(messages, str):
            if isinstance(self.history, list):
                messages = self.history + [Message(role=Role.user, content=messages).model_dump(mode="json")]
                self.history = messages
            else:
                messages = [Message(role=Role.user, content=messages).model_dump(mode="json")]
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
            "messages": messages,
            "thinking": self.thinking,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        if response_model is not None:
            tools = [{
                "name": "respond",
                "description": "Respond to the user's message.",
                "input_schema": response_model.model_json_schema()
            }]
            args["tools"] = tools
            args["tool_choice"] = {"type": "tool", "name": "respond"}
        if self.mcp_config is not None:
            args["mcp_servers"] = [self.mcp_config]
            args["betas"] = ["mcp-client-2025-04-04"]
            response = self.client.beta.messages.create(**args).content
        else:
            response = self.client.messages.create(**args).content
        if len(response) < 1:
            response = {"type": "text", "text": ""}
        else:
            response = response[0]
        if response.type == "text":
            result = response.text
        elif response.type == "tool_use":
            result = response_model.model_validate(response.input)
        if isinstance(self.history, list):
            content = json.dumps(result.model_dump(mode="json")) if isinstance(result, BaseModel) else str(result)
            self.history.append(Message(role=Role.model, content=content).model_dump(mode="json"))
        return result