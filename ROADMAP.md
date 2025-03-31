## todo/roadmap/ideas
steps:
- search, delete, load (defaults)
- more data types (one fvecs next)
- embedding model (simple abstraction)
    - be able to load an alreayd existing model
    that is commonly used
    - look into a custom embedding model as well tho
    - try to be completely from scratch no pytorch

- goal 2: embedding model pipeline, process docs
- goal 3: connect with a model downloaded via huggingface lib
- goal 4: fully connected via bindings in helix (option for no http)

- another cool idea: speech models, feed in everything you have and talk
    to a model about anything while it pulls into context, knowledge from
    docs and such to enhance responses (talking with grok is so cool)

- ex: simple run with llama3.2:1b
- ex: simple run in backend server with flask
- ex: loading data from huggingface and working with that

- comment all functions so documentation is super easy
- write tests for everything
- write all need to be fast text processing in c (tokenizer, chunker) for loader

## rag pipeline ideas
```python
app = helix.RAGApp()
app.add_document_store("my_docs/", chunker=helix.chunkers.Semantic())
app.set_embedder("BAAI/bge-large-en-v1.5")
app.set_retriever(helix.retrievers.Hybrid(top_k=5))
app.set_llm("meta-llama/Llama-3-8b-instruct")
response = app.query("How does photosynthesis work?")
```

```python
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
```