from chonkie import TokenChunker
from typing import List, Optional, Union, Any

class Chunk:
    def __init__(self, text: str, start_index: int = 0, end_index: int = 0, token_count: int = 0):
        self.text = text
        self.start_index = start_index
        self.end_index = end_index
        self.token_count = token_count

    
    @staticmethod
    def token_chunk(text: Union[str, List[str]], chunk_size: int = 2048, chunk_overlap: int = 12, tokenizer: Optional[Any] = None) -> Union[List['Chunk'], List[List['Chunk']]]:
        if tokenizer:
            chunker = TokenChunker(tokenizer=tokenizer, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        else:
            chunker = TokenChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        
        # check if text is a string or a list of strings
        if isinstance(text, str):
            # if string then can do single text chunking
            chonkie_chunks = chunker.chunk(text)
            return [Chunk(chunk.text, chunk.start_index, chunk.end_index, chunk.token_count) for chunk in chonkie_chunks]
        else:
            # if list then can do chunk batch
            batch_chunks = chunker.chunk_batch(text)
            return [[Chunk(chunk.text, chunk.start_index, chunk.end_index, chunk.token_count) for chunk in doc_chunks] 
                    for doc_chunks in batch_chunks]
