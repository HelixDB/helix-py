from helix.embedding.embedder import Embedder
from helix.types import GHELIX
import voyageai
from typing import List
from tqdm import tqdm
from dotenv import load_dotenv
import sys
import os

DEFAULT_MODEL = "voyage-3.5"
DEFAULT_DIMENSIONS = 1024

class VoyageAIEmbedder(Embedder):
    """
    VoyageAI Embedder

    Args:
        api_key (str): The API key for VoyageAI. (Defaults to VOYAGEAI_API_KEY environment variable)
        model (str): The model to use.
        dimensions (int): The dimensions of the embedding.
    """
    def __init__(self, api_key: str=None, model: str=DEFAULT_MODEL, dimensions: int=DEFAULT_DIMENSIONS):
        if api_key is None:
            load_dotenv()
            api_key = os.getenv("VOYAGEAI_API_KEY")
            if api_key is None:
                raise ValueError("API key not provided and VOYAGEAI_API_KEY environment variable not set.")
        self.client = voyageai.Client(api_key=api_key)
        self.model = model
        self.dimensions = dimensions
    
    def embed(self, data: str, input_type: str=None) -> List[float]:
        """
        Embed a string using VoyageAI.

        Args:
            data (str): The string to embed.
            input_type (str, optional): The input type to use. (eg. query, document)

        Returns:
            List[float]: The embedding of the string.
        """
        args = {"texts": [data], "model": self.model, "output_dimension": self.dimensions}
        if input_type is not None:
            args["input_type"] = input_type
        return self.client.embed(**args).embeddings[0]

    def embed_batch(self, data_list: List[str], input_type: str=None) -> List[List[float]]:
        """
        Embed a list of strings using VoyageAI.

        Args:
            data_list (List[str]): The list of strings to embed.
            input_type (str, optional): The input type to use. (eg. query, document)

        Returns:
            List[List[float]]: The list of embeddings.
        """
        args = {"texts": data_list, "model": self.model, "output_dimension": self.dimensions}
        if input_type is not None:
            args["input_type"] = input_type
        return [embedding for embedding in tqdm(self.client.embed(**args).embeddings, total=len(data_list), desc=f"{GHELIX} Embedding", file=sys.stderr)]