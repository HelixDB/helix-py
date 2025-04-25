# note: first run examples/rag_demo/load_docs.py
import helix
from helix.client import ragfetch
import requests
from transformers import BertTokenizer, BertModel
import torch

db = helix.Client(local=True)

tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
model = BertModel.from_pretrained("bert-base-uncased")

OLLAMA_API_URL = "http://localhost:11434/api/generate"

def get_ollama_response(prompt):
    payload = {
        "model": "llama3.2:3b",
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(OLLAMA_API_URL, json=payload)
    if response.status_code == 200:
        return response.json()["response"]
    else:
        raise Exception(f"Ollama API request failed with status {response.status_code}")

def vectorize_prompt(prompt):
    """Convert prompt to BERT embedding."""
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
        # Use the [CLS] token embedding as the prompt representation
        embedding = outputs.last_hidden_state[:, 0, :].squeeze().numpy()
    return embedding

def prompt_loop():
    while True:
        user_prompt = input("user: ").strip()
        if user_prompt.lower() == "quit":
            break

        reformat_prompt = f"Convert the following question into a concise query for retrieving Rust documentation: {user_prompt}"
        reformatted_query = get_ollama_response(reformat_prompt)
        print(f"\nReformatted Query: {reformatted_query}")

        vectorized_prompt = vectorize_prompt(reformatted_query)

        doc = db.query(ragfetch(vectorized_prompt))
        print(f"\nRetrieved Document: {doc[:200]}...")

        response_prompt = f"Based on the following documentation, answer the question: {user_prompt}\n\nDocumentation: {doc}"
        response = get_ollama_response(response_prompt)

        print("\nresponse: ")
        print(response)
        print("\n")

if __name__ == "__main__":
    prompt_loop()
