#!/usr/bin/env python3
import helix
from helix import Hnode, Hedge, Hvector, json_to_helix
from chonkie import RecursiveRules, RecursiveLevel, RecursiveChunker, SemanticChunker
import pymupdf4llm
import argparse
from typing import List
import torch
from transformers import AutoTokenizer, AutoModel
from tqdm import tqdm
import requests

"""
embed_model = "albert-base-v2"
tokenizer = AutoTokenizer.from_pretrained(embed_model)
model = AutoModel.from_pretrained(embed_model)

def vectorize_text(text) -> List[float]:
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
        embedding = outputs.last_hidden_state[:, 0, :].squeeze().tolist()
    return embedding

def vectorize_chunked(chunked: List[str]) -> List[List[float]]:
    return [vectorize_text(chunk) for chunk in tqdm(chunked)]
"""

def chunker(text: str, chunk_style: str="recursive", chunk_size: int=100):
    chunked_text = ""
    match chunk_style.lower():
        case "recursive":
            rules = RecursiveRules(
                    levels=[
                        RecursiveLevel(delimiters=['######', '#####', '####', '###', '##', '#']),
                        RecursiveLevel(delimiters=['\n\n', '\n', '\r\n', '\r']),
                        RecursiveLevel(delimiters='.?!;:'),
                        RecursiveLevel()
                        ]
                    )
            chunker = RecursiveChunker(rules=rules, chunk_size=chunk_size)
            chunked_text = chunker(text)

        case "semantic":
            chunker = SemanticChunker(
                    embedding_model="minishlab/potion-base-8M",
                    threshold="auto",
                    chunk_size=chunk_size,
                    min_sentences=1
            )
            chunked_text = chunker(text)

        case _:
            raise RuntimeError("unknown chunking style")

    [print(c, "\n--------\n") for c in chunked_text]
    return [c.text for c in chunked_text]

def convert_to_markdown(path: str, doc_type: str) -> str:
    if doc_type not in ["pdf", "csv"]:
        raise RuntimeError("unknown doc type")

    md_convert = None
    if path.endswith(".pdf") and doc_type == "pdf":
        md_convert = pymupdf4llm.to_markdown(path)
    return str(md_convert)

# TODO: future would be cool with some sort of tool call
def gen_n_and_e(chunks: str):
    prompt = """You are task is to only produce json structured output and nothing else. Do no
        provide any extra commentary or text. Based on the following sentence/s, split it into
        node entities and edge connections by simply defining Node(label) and Edge(label). Only
        create nodes based on people, things, ideas and edges based on adjectives and verbs. Avoid
        at all costs classifying any useless/fluff parts in the chunk of text. Here is an example
        of what you should produce:
        {
              "Nodes": [
                {
                  "Label": "Woman"
                }
              ],
              "Edges": [
                {
                  "Label": "Husband-Wife",
                  "Source": "Woman",
                  "Target": "Pierre Curie"
                }
            ]
        }
        Now do this on this text:
    """
    return [get_ollama_response(prompt + chunk) for chunk in chunks]

# for now just use ollama, but hook up to openai soon
OLLAMA_API_URL = "http://localhost:11434/api/generate"

def get_ollama_response(prompt):
    payload = {
        "model": "mistral:latest",
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(OLLAMA_API_URL, json=payload)
    if response.status_code == 200:
        return response.json()["response"]
    else:
        raise Exception(f"ollama api request failed with status {response.status_code}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="helix knowledge workflow")
    parser.add_argument("input", help="input file path", nargs=1)
    parser.add_argument("-t", "--type", help="input doc type (pdf, ...)", default="pdf")
    parser.add_argument("-c", "--chunking_method", help="chunking method (recursive, semantic", default="recursive")
    args = parser.parse_args()

    in_doc = args.input[0]
    doc_type = args.type
    chunking_method = args.chunking_method

    # testing
    sample_text = """
        Marie Curie, 7 November 1867 – 4 July 1934, was a Polish and naturalised-French physicist and chemist who conducted pioneering research on radioactivity.
        She was the first woman to win a Nobel Prize, the first person to win a Nobel Prize twice, and the only person to win a Nobel Prize in two scientific fields.
        Her husband, Pierre Curie, was a co-winner of her first Nobel Prize, making them the first-ever married couple to win the Nobel Prize and launching the Curie family legacy of five Nobel Prizes.
        She was, in 1906, the first woman to become a professor at the University of Paris.
        Also, Robin Williams.
    """

    md_text = convert_to_markdown(in_doc, doc_type)
    chunked_text = chunker(md_text, chunking_method)
    gened = gen_n_and_e(chunked_text)
    l_nodes_edges = [json_to_helix(gen) for gen in gened]
    for nodes, edges in l_nodes_edges:
        print(nodes, edges)

