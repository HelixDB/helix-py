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

def vectorize_text(text: str) -> List[float]:
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
        embedding = outputs.last_hidden_state[:, 0, :].squeeze().tolist()
    return embedding

@app.post("/embed")
async def get_embedding(input: TextInput):
    try:
        embedding = vectorize_text(input.text)
        return {"embedding": embedding}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8699)

