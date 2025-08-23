from .embedder import Embedder
from openai import OpenAI
from typing import List
from tqdm import tqdm
import sys

DEFAULT_MODEL = "text-embedding-3-small"
DEFAULT_DIMENSIONS = 1536

class OpenAIEmbedder(Embedder):
    def __init__(self, api_key: str, model: str=DEFAULT_MODEL, dimensions: int=DEFAULT_DIMENSIONS):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.dimensions = dimensions

    def embed(self, data: str) -> List[float]:
        return self.client.embeddings.create(input=data, model=self.model, dimensions=self.dimensions).data[0].embedding

    def embed_batch(self, data_list: List[str]) -> List[List[float]]:
        return [vector.embedding for vector in tqdm(self.client.embeddings.create(input=data_list, model=self.model, dimensions=self.dimensions).data, total=len(data_list), desc="Embedding", file=sys.stderr)]