# rag pipeline ideas
"""
app = helix.RAGApp()
app.add_document_store("my_docs/", chunker=helix.chunkers.Semantic())
app.set_embedder("BAAI/bge-large-en-v1.5")
app.set_retriever(helix.retrievers.Hybrid(top_k=5))
app.set_llm("meta-llama/Llama-3-8b-instruct")
response = app.query("How does photosynthesis work?")

class RAGPipeline:
    def __init__(self, embedding_model: ModelLoader, language_model: ModelLoader,
                 vector_db: helix.Client, chunking: Chunking):
        self.embedding_model = embedding_model
        self.language_model = language_model
        self.vector_db = vector_db
        self.chunking = chunking

    def ingest_data(self, documents: List[str]):
        for doc in documents:
            chunks = self.chunking.chunk(doc)
            for chunk in chunks:
                vector = self.embedding_model.embed(chunk)
                metadata = {"text": chunk}
                self.vector_db.query(InsertVector(vector, metadata))

    def query(self, user_query: str, k: int = 5) -> str:
        query_vector = self.embedding_model.embed(user_query)
        results = self.vector_db.query(SearchVectors(query_vector, k))
        retrieved_texts = [result["metadata"]["text"] for result in results]
        prompt = f"Query: {user_query}\nContext:\n{' '.join(retrieved_texts)}\nResponse:"
        return self.language_model.generate(prompt)
"""

# ex: simple run with llama3.2:1b
# ex: simple run in backend server with flask

# TODO: probably actually not going to build in the embedder
#   for now, want just a very basic lib for interfacing with helix-db
#   as well as some tokenization and chunking abilites, no more than
#   numpy and pyarrow for now

# TODO: custom write version we need
#   all AutoTokenizer does is pull the model
#   all model(**inputs) does is run it through via pytorch
#   def gonna still need pytorch for some time
# something like this too:
"""

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
"""
