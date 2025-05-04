# note: first run python examples/rag_demo/load_docs.py
import helix
from helix.client import ragsearchdocs

import requests
import torch
import sys
from transformers import AutoTokenizer, AutoModel

sys.stdout.flush()

db = helix.Client(local=True)

tokenizer = AutoTokenizer.from_pretrained("allenai/scibert_scivocab_uncased")
model = AutoModel.from_pretrained("allenai/scibert_scivocab_uncased")

OLLAMA_API_URL = "http://localhost:11434/api/generate"

def get_ollama_response(prompt):
    payload = {
        #"model": "deepseek-r1:7b",
        "model": "llama3.1:8b",
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(OLLAMA_API_URL, json=payload)
    if response.status_code == 200:
        return response.json()["response"]
    else:
        raise Exception(f"Ollama API request failed with status {response.status_code}")

def vectorize_prompt(prompt):
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
        embedding = outputs.last_hidden_state[:, 0, :].squeeze().tolist()
    return embedding

def create_prompt(user_prompt: str, context):
    reformated_prompt = f"""<instructions>
    Based on the provided contexts, answer the given question to the best of your ability. Answer only from the given context, and if there's no appropriate context, reply "No relevant context found!".
    </instructions>

    <context>
    {context}
    </context>

    <query>
    {user_prompt}
    </query>
    """

    return reformated_prompt

def prompt_loop():
    while True:
        user_prompt = input("user: ").strip()
        if user_prompt.lower() == "quit": break

        reformat_prompt = f"""Convert the following question into a concise query that resembles snippets of rust documentation from the rust book
        for retrieving Rust documentation. You should ideally recognize all possible key words related to this. Do not give long code snippets
        just a couple of sentences using keywords related to the question asked. Don't add any extra new lines and stuff. Should not be longer
        than 200 words: {user_prompt}"""
        reformatted_query = get_ollama_response(reformat_prompt)
        print(f"\nReformatted query: {reformatted_query}")

        vectorized_prompt = vectorize_prompt(user_prompt)

        docs = db.query(ragsearchdocs(vectorized_prompt, 6))
        for doc in docs[0]:
            print(doc)
            print("\n\n\n\n")

        response = get_ollama_response(create_prompt(user_prompt, docs))

        print("\nresponse: ")
        print(response)
        print("\n")

if __name__ == "__main__":
    prompt_loop()