#!/usr/bin/env python3
import helix
from helix import hnswinsert
from chonkie import RecursiveRules, RecursiveLevel, RecursiveChunker, SemanticChunker
import pymupdf4llm
import argparse
from typing import List
import torch
from transformers import AutoTokenizer, AutoModel
from tqdm import tqdm
import os

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

    return [c.text for c in chunked_text]

def convert_to_markdown(path: str, doc_type: str) -> str:
    if doc_type not in ["pdf", "csv", "markdown", "txt"]:
        raise RuntimeError("unknown doc type")

    if not os.path.exists(path):
        raise FileNotFoundError(f"file not found: {path}")

    md_convert = None
    if path.endswith(".pdf") and doc_type == "pdf":
        try:
            md_convert = pymupdf4llm.to_markdown(path)
        except Exception as e:
            raise RuntimeError(f"failed to convert pdf: {e}")

    elif path.endswith(".md") and doc_type == "markdown":
        with open(path, 'r', encoding='utf-8') as file:
            md_convert = file.read()

    return str(md_convert)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="helix knowledge workflow")
    parser.add_argument("input", help="input file path", nargs=1)
    parser.add_argument("-t", "--type", help="input doc type (pdf, ...)", default="pdf")
    parser.add_argument("-c", "--chunking_method", help="chunking method (recursive, semantic", default="recursive")
    parser.add_argument("-cs", "--chunking_size", help="number of characters per chunk", default=100)
    args = parser.parse_args()

    #client = helix.Client(local=True)

    in_doc = args.input[0]
    doc_type = args.type
    chunking_method = args.chunking_method
    chunking_size = args.chunking_size

    md_text = convert_to_markdown(str(in_doc), doc_type)
    chunked_text = chunker(md_text, chunking_method, int(chunking_size))
    embedded_chunks = vectorize_chunked(chunked_text)

    proced_data = zip(chunked_text, embedded_chunks)
    for txt, vec in proced_data:
        print(txt, vec)
        print("--------------")

