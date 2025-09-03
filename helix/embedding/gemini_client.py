from helix.embedding.embedder import Embedder
from helix.types import GHELIX
from google import genai
from google.genai import types
from typing import List
from tqdm import tqdm
from dotenv import load_dotenv
import sys
import os

DEFAULT_MODEL = "gemini-embedding-001"
DEFAULT_DIMENSIONS = 1536
MAX_BATCH_SIZE = 100

class GeminiEmbedder(Embedder):
    """
    Gemini Embedder

    Args:
        api_key (str): The API key for Gemini. (Defaults to GEMINI_API_KEY environment variable)
        model (str): The model to use.
        dimensions (int): The dimensions of the embedding.
    """
    def __init__(self, api_key: str=None, model: str=DEFAULT_MODEL, dimensions: int=DEFAULT_DIMENSIONS):
        if api_key is None:
            load_dotenv()
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key is None:
                raise ValueError("API key not provided and GEMINI_API_KEY environment variable not set.")
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.dimensions = dimensions
    
    def embed(self, data: str, task_type: str=None) -> List[float]:
        """
        Embed a string using Gemini.

        Args:
            data (str): The string to embed.
            task_type (str, optional): The task type to use. (eg. SEMANTIC_SIMILARITY)

        Returns:
            List[float]: The embedding of the string.
        """
        config = types.EmbedContentConfig(output_dimensionality=self.dimensions)
        if task_type is not None:
            config.task_type = task_type
        return self.client.models.embed_content(contents=[data], model=self.model, config=config).embeddings[0].values

    def embed_batch(self, data_list: List[str], task_type: str=None) -> List[List[float]]:
        """
        Embed a list of strings using Gemini.

        Args:
            data_list (List[str]): The list of strings to embed.
            task_type (str, optional): The task type to use. (eg. SEMANTIC_SIMILARITY)

        Returns:
            List[List[float]]: The list of embeddings.
        """
        config = types.EmbedContentConfig(output_dimensionality=self.dimensions)
        if task_type is not None:
            config.task_type = task_type
        embeddings = []
        pbar = tqdm(total=len(data_list), desc=f"{GHELIX} Embedding", file=sys.stderr)
        for i in range(0, len(data_list), MAX_BATCH_SIZE):
            response = self.client.models.embed_content(contents=data_list[i:i+MAX_BATCH_SIZE], model=self.model, config=config)
            for embedding in response.embeddings:
                embeddings.append(embedding.values)
                pbar.update(1)
        pbar.close()
        return embeddings