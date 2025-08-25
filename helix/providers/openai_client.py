from helix.providers.provider import Provider
from agents import Agent, ModelSettings, Runner, AgentOutputSchema
from openai.types.shared import Reasoning
from agents.mcp import MCPServerStreamableHttp
from pydantic import BaseModel
from enum import Enum
from typing import List, Any, Literal
from dotenv import load_dotenv
import json
import os
import asyncio

DEFAULT_MODEL = "gpt-5-nano"
DEFAULT_MCP_URL = "http://localhost:8000/mcp/"

class Role(Enum):
    user = "user"
    model = "assistant"

class Message(BaseModel):
    role: Role
    content: Any | None = None

class OpenAIProvider(Provider):
    """
    OpenAI LLM Provider

    Args:
        name (str): The name of the agent.
        instructions (str): The instructions for the agent.
        model (str): The model to use.
        temperature (float): The temperature setting to use. (Not supported for gpt-5 models)
        reasoning (Reasoning | None): The reasoning setting to use. (Only supported for gpt-5 models)
        verbosity (Literal["low", "medium", "high"] | None): The verbosity level to use.
        history (bool): Whether to use history.
    """

    def __init__(
        self,
        name: str,
        instructions: str,
        model: str = DEFAULT_MODEL,
        temperature: float | None = None,
        reasoning: Reasoning | None = None,
        verbosity: Literal["low", "medium", "high"] | None = None,
        history: bool = False,
    ):
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key is None:
            raise ValueError("API key not provided and OPENAI_API_KEY environment variable not set.")

        self.agent_configs = {
            "name": name,
            "instructions": instructions,
            "model": model,
            "model_settings": ModelSettings(
                temperature=temperature,
                reasoning=reasoning,
                verbosity=verbosity
            )
        }

        self.history = [] if history else None
        self.mcp_server_config = None

    def enable_mcps(
        self,
        name: str,
        url: str = DEFAULT_MCP_URL,
    ) -> bool:
        """
        Enable MCPs for the OpenAI provider.

        Args:
            name (str): The name of the server.
            url (str, optional): The URL of the server. (Defaults to "http://localhost:8000/mcp/")

        Returns:
            bool: True if MCPs are enabled, False otherwise.
        """
        self.mcp_server_config = {"url": url, "name": name}
        return True

    def generate(
        self, 
        messages: str | List[Message] | List[dict], 
        response_model: BaseModel | None = None,
    ) -> str | BaseModel:
        """
        Generate a response from the OpenAI provider.

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

        if response_model is not None:
            self.agent_configs["output_type"] = AgentOutputSchema(
                output_type=response_model,
            )
        else:
            self.agent_configs.pop("output_type", None)
        
        async def gen():
            if self.mcp_server_config:
                async with MCPServerStreamableHttp(
                    name=self.mcp_server_config["name"],
                    params={"url": self.mcp_server_config["url"]}
                ) as server:
                    agent_configs = self.agent_configs.copy()
                    agent_configs["mcp_servers"] = [server]
                    agent_configs["mcp_config"] = {"convert_schemas_to_strict": True}
                    agent = Agent(**agent_configs)
                    return await Runner.run(starting_agent=agent, input=messages)
            else:
                agent = Agent(**self.agent_configs)
                return await Runner.run(starting_agent=agent, input=messages)
        
        response = asyncio.run(gen())
        if response_model is not None:
            result = response_model.model_validate(response.final_output)
        else:
            result = response.final_output
        if isinstance(self.history, list):
            content = json.dumps(result.model_dump(mode="json")) if isinstance(result, BaseModel) else str(result)
            self.history.append(Message(role=Role.model, content=content).model_dump(mode="json"))
        return result