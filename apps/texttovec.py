from chonkie import RecursiveRules, RecursiveLevel, RecursiveChunker, SemanticChunker
from typing import List
import torch
from transformers import AutoTokenizer, AutoModel
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI()
embed_model = "albert-base-v2"
tokenizer = AutoTokenizer.from_pretrained(embed_model)
model = AutoModel.from_pretrained(embed_model)

class TextInput(BaseModel):
    text: str
    chunk_style: str = "recursive"
    chunk_size: int = 100

def vectorize_text(text) -> List[float]:
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
        embedding = outputs.last_hidden_state[:, 0, :].squeeze().tolist()
    return embedding

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

@app.post("/embed")
async def get_embedding(input: TextInput):
    try:
        chunked_text = chunker(input.text, input.chunk_style, input.chunk_size)
        embedded_chunks = [vectorize_text(chunk) for chunk in chunked_text]
        return {"chunks": chunked_text, "embeddings": embedded_chunks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8699)

