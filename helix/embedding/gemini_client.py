from helix.embedding.embedder import Embedder
from helix.types import GHELIX
from google import genai
from google.genai import types
from typing import List
from tqdm import tqdm
import sys
import os

DEFAULT_MODEL = "gemini-embedding-001"
DEFAULT_DIMENSIONS = 1536

class GeminiEmbedder(Embedder):
    def __init__(self, api_key: str=None, model: str=DEFAULT_MODEL, dimensions: int=DEFAULT_DIMENSIONS, base_url: str=None):
        if api_key is None:
            api_key = os.environ.get("GEMINI_API_KEY")
            if api_key is None:
                raise ValueError("API key not provided and GEMINI_API_KEY environment variable not set.")
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.dimensions = dimensions
    
    def embed(self, data: str, task_type: str=None) -> List[float]:
        config = types.EmbedContentConfig(output_dimensionality=self.dimensions)
        if task_type is not None:
            config.task_type = task_type
        return self.client.models.embed_content(contents=[data], model=self.model, config=config).embeddings[0].values

    def embed_batch(self, data_list: List[str], task_type: str=None) -> List[List[float]]:
        config = types.EmbedContentConfig(output_dimensionality=self.dimensions)
        if task_type is not None:
            config.task_type = task_type
        return [embedding.values for embedding in tqdm(self.client.models.embed_content(contents=data_list, model=self.model, config=config).embeddings, total=len(data_list), desc=f"{GHELIX} Embedding", file=sys.stderr)]