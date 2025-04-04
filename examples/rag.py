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