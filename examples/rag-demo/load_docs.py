# Load all docs into helix
# - chunk input document
# - vectorize input text
# - db.query load all the chunked+vectorized texts + input document

import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
import numpy as np

def fetch_rust_docs(urls):
    """Fetch and extract text from Rust documentation pages."""
    documents = []
    for url in urls:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch {url}")
            continue
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract text from paragraphs
        paragraphs = soup.find_all('p')
        text = " ".join(p.get_text().strip() for p in paragraphs if p.get_text().strip())
        if text:
            documents.append(text)
    return documents

def chunk_text(text, max_length=500):
    """Split text into chunks of approximately max_length characters."""
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        current_length += len(word) + 1
        if current_length > max_length:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_length = len(word) + 1
        else:
            current_chunk.append(word)
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

def ingest_documents(documents, model, db_url="http://localhost:6969/insertdoc"):
    """Chunk documents, generate embeddings, and insert into database."""
    for doc in documents:
        chunks = chunk_text(doc)
        if not chunks:
            continue
        embeddings = model.encode(chunks, convert_to_numpy=True)
        for chunk, embedding in zip(chunks, embeddings):
            payload = {
                "text": chunk,
                "embedding": embedding.tolist()
            }
            try:
                response = requests.post(db_url, json=payload)
                if response.status_code != 200:
                    print(f"Failed to insert chunk: {response.text}")
                else:
                    print(f"Inserted chunk: {chunk[:50]}...")
            except requests.RequestException as e:
                print(f"Error inserting chunk: {e}")

def verify_insertion(model, query, db_url="http://localhost:6969/searchdoc"):
    """Verify database insertion by querying with a sample query."""
    query_embedding = model.encode([query], convert_to_numpy=True)[0]
    payload = {"embedding": query_embedding.tolist()}
    try:
        response = requests.post(db_url, json=payload)
        if response.status_code == 200:
            docs = response.json()
            print(f"Sample query results: {docs}")
        else:
            print(f"Verification failed: {response.text}")
    except requests.RequestException as e:
        print(f"Verification error: {e}")

def main():
    # Initialize BERT model
    bert_model = SentenceTransformer('all-MiniLM-L6-v2')

    # Define Rust documentation URLs (example pages from The Rust Book)
    rust_doc_urls = [
        "https://doc.rust-lang.org/book/ch01-01-installation.html",
        "https://doc.rust-lang.org/book/ch01-02-hello-world.html"
    ]

    # Step 1: Fetch Rust documentation
    print("Fetching Rust documentation...")
    documents = fetch_rust_docs(rust_doc_urls)
    if not documents:
        print("No documents fetched. Exiting.")
        return

    # Step 2 & 3 & 4: Chunk, vectorize, and insert
    print("Ingesting documents into database...")
    ingest_documents(documents, bert_model)

    # Step 5: Verify insertion
    print("Verifying database insertion...")
    sample_query = "What is Rust programming?"
    verify_insertion(bert_model, sample_query)

if __name__ == "__main__":
    main()
