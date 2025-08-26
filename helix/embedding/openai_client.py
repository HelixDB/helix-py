from helix.embedding.embedder import Embedder
from helix.types import GHELIX
from openai import OpenAI
from typing import List
from tqdm import tqdm
from dotenv import load_dotenv
import sys
import os

DEFAULT_MODEL = "text-embedding-3-small"
DEFAULT_DIMENSIONS = 1536

class OpenAIEmbedder(Embedder):
    """
    OpenAI Embedder

    Args:
        api_key (str): The API key for OpenAI. (Defaults to OPENAI_API_KEY environment variable)
        model (str): The model to use.
        dimensions (int): The dimensions of the embedding.
        base_url (str): The base URL for the OpenAI API. 
    """
    def __init__(self, api_key: str=None, model: str=DEFAULT_MODEL, dimensions: int=DEFAULT_DIMENSIONS, base_url: str=None):
        if api_key is None:
            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key is None:
                raise ValueError("API key not provided and OPENAI_API_KEY environment variable not set.")
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.dimensions = dimensions

    def embed(self, data: str) -> List[float]:
        """
        Embed a string using OpenAI.

        Args:
            data (str): The string to embed.

        Returns:
            List[float]: The embedding of the string.
        """
        return self.client.embeddings.create(input=data, model=self.model, dimensions=self.dimensions).data[0].embedding

    def embed_batch(self, data_list: List[str]) -> List[List[float]]:
        """
        Embed a list of strings using OpenAI.

        Args:
            data_list (List[str]): The list of strings to embed.

        Returns:
            List[List[float]]: The list of embeddings.
        """
        return [vector.embedding for vector in tqdm(self.client.embeddings.create(input=data_list, model=self.model, dimensions=self.dimensions).data, total=len(data_list), desc=f"{GHELIX} Embedding", file=sys.stderr)]