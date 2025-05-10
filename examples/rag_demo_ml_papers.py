# 1. python3 -m venv venv
# 2. source venv/bin/activate
# 3. pip install chonkie docling torch transformers tqdm requests helix-py

from helix import Client, Query, Payload
from typing import List, Tuple

from chonkie import RecursiveChunker, RecursiveRules, RecursiveLevel
from docling.document_converter import DocumentConverter
from transformers.models.auto.modeling_auto import AutoModel
from transformers.models.auto.tokenization_auto import AutoTokenizer
from tqdm import tqdm
import torch

tokenizer = AutoTokenizer.from_pretrained("allenai/scibert_scivocab_uncased")
model = AutoModel.from_pretrained("allenai/scibert_scivocab_uncased")

class ragloaddocs(Query):
    def __init__(self, docs: List[Tuple[str, List[Tuple[List[float], str]]]]):
        super().__init__()
        self.docs = docs
    def query(self) -> List[Payload]:
        docs_payload = []
        for doc, vectors in self.docs:
            docs_payload.append({ "doc": doc, "vectors": [{ "vec": vec, "chunk": chunk } for vec, chunk in vectors]})
        return [{ "docs": docs_payload }]
    def response(self, response): return response

class ragsearchdocs(Query):
    def __init__(self, query_vector: List[float], k: int=4):
        super().__init__()
        self.query_vector = query_vector
        self.k = k
    def query(self) -> List[Payload]: return [{ "query": self.query_vector, "k": self.k }]
    def response(self, response): return response.get("chunks")

def vectorize_text(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
        embedding = outputs.last_hidden_state[:, 0, :].squeeze().tolist()
    return embedding

def fetch_papers():
    print("fetching papers...")
    papers = [
        "https://arxiv.org/pdf/1706.03762", # transformers paper
        "https://arxiv.org/pdf/1607.06450", # layer norm paper
        "https://arxiv.org/pdf/1301.3781", # word2vec paper
        "https://arxiv.org/pdf/2005.11401", # rag paper
        "https://arxiv.org/pdf/1409.3215", # sequence to sequence learning paper
    ]
    converter = DocumentConverter()
    results = [converter.convert(paper) for paper in tqdm(papers, desc="converting papers")]
    text_results = [res.document.export_to_markdown() for res in results]
    return text_results

def process_papers():
    text_papers = fetch_papers()

    print("loading papers...")
    rules = RecursiveRules(
        levels=[
            RecursiveLevel(delimiters=['######', '#####', '####', '###', '##', '#']),
            RecursiveLevel(delimiters=['\n\n', '\n', '\r\n', '\r']),
            RecursiveLevel(delimiters='.?!;:'),
            RecursiveLevel()
        ]
    )

    print("chunking papers...")
    chunker = RecursiveChunker(rules=rules, chunk_size=250)
    papers_chunks = [[chunk.text for chunk in chunker(paper)] for paper in text_papers]
    #[print(f"doc[{i}], num of chunks: {len(chunks)}\nfirst 3 chunks:\n{chunks[:3]}") for i, chunks in enumerate(papers_chunks)]
    print("chunked and loaded papers")
    return list(zip(text_papers, papers_chunks)) # List[Tuple[str, Sequence[Chunk]]]

def load(db: Client):
    papers = process_papers()
    docs = []
    for paper, chunks in papers:
        vectors = [vectorize_text(chunk) for chunk in tqdm(chunks, desc="vectorizing")]
        docs.append((paper, list(zip(vectors, chunks))))

    res =db.query(ragloaddocs(docs))
    print(f"helix load response: {res[0]}")

def query(db: Client):
    print("querying...")
    queries = [
        "what is attention as it relates to transformers and how does it work?",
        "how does layer normalization work with regards to normalizing neural network weights?",
        "why is the word2vec model usefule and what neural network architecture does it use?",
        "how can I use 0retrieval augmented generation and how does work with large lanuage models?",
        "what is sequence to sequence learning?",
    ]

    for query in queries:
        res = db.query(ragsearchdocs(vectorize_text(query), 6))[0]
        res_text = '\n'.join([f"Chunk[{i+1}]:\n{r['content']}" for i, r in enumerate(res)])
        print(f"-----------\nquery: {query}\nfetched:\n{res_text}")

if __name__ == "__main__":
    db = Client(local=True)

    load(db)
    query(db)