from abc import ABC, abstractmethod
from typing import List
from helix.loader import Loader

# TODO: custom write version we need
#   all AutoTokenizer does is pull the model
#   all model(**inputs) does is run it through via pytorch
#   def gonna still need pytorch for some time
from transformers import AutoModel, AutoTokenizer
import torch

class Embedder(ABC):
    @abstractmethod
    def embed(self, text: str) -> List[float]: pass

    @abstractmethod
    def batch_embed(self, texts: List[str]) -> List[List[float]]: pass

# for now default, but can write custom ones
class EmbeddingModel(Embedder):
    def __init__(self, model_name: str="bert-base-uncased"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()

    def embed(self, text: str) -> List[float]:
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
            cls_embedding = outputs.last_hidden_state[:, 0, :].squeeze(0) # use [CLS] token embedding
        return cls_embedding.tolist()

    def batch_embed(self, texts: Loader) -> List[List[float]]:
        inputs = self.tokenizer(texts.get_data(), return_tensors="pt", truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
            cls_embeddings = outputs.last_hidden_state[:, 0, :]
        return cls_embeddings.tolist()