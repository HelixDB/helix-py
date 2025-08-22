from chonkie import TokenChunker, SentenceChunker, RecursiveChunker, RecursiveRules
from typing import List, Optional, Union, Any
from tokenizers import Tokenizer

class Chunk:
    def __init__(self, text: str, start_index: int = 0, end_index: int = 0, token_count: int = 0):
        self.text = text
        self.start_index = start_index
        self.end_index = end_index
        self.token_count = token_count

    # this method helps handle the common chunking logic e.g single text or batch text
    @staticmethod
    def _process_chunks(chunker, text: Union[str, List[str]]) -> Union[List['Chunk'], List[List['Chunk']]]:
        if isinstance(text, str):
            chonkie_chunks = chunker.chunk(text)
            return [Chunk(chunk.text, chunk.start_index, chunk.end_index, chunk.token_count) for chunk in chonkie_chunks]
        else:
            batch_chunks = chunker.chunk_batch(text)
            return [[Chunk(chunk.text, chunk.start_index, chunk.end_index, chunk.token_count) for chunk in doc_chunks] 
                    for doc_chunks in batch_chunks]
    
    # this is for chonkie token chunker
    @staticmethod
    def token_chunk(text: Union[str, List[str]], chunk_size: int = 2048, chunk_overlap: int = 12, tokenizer: Optional[Any] = None) -> Union[List['Chunk'], List[List['Chunk']]]:
        if tokenizer:
            custom_tokenizer = Tokenizer.from_pretrained(tokenizer)
            chunker = TokenChunker(tokenizer=custom_tokenizer, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        else:
            chunker = TokenChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        
        return Chunk._process_chunks(chunker, text)

    # this is for chonkie sentence chunker
    @staticmethod
    def sentence_chunk(text: Union[str, List[str]], tokenizer: str = "character", chunk_size: int = 2048, chunk_overlap: int = 12, min_sentences_per_chunk: int = 1) -> Union[List['Chunk'], List[List['Chunk']]]:
        chunker = SentenceChunker(
            tokenizer_or_token_counter=tokenizer,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            min_sentences_per_chunk=min_sentences_per_chunk
        )
        
        return Chunk._process_chunks(chunker, text)

    # this is for chonkie recursive chunker
    @staticmethod
    def recursive_chunk(text: Union[str, List[str]], tokenizer: str = "character", chunk_size: int = 2048, 
                       rules: Optional[Any] = None, min_characters_per_chunk: int = 24, 
                       recipe: Optional[str] = None, lang: str = "en") -> Union[List['Chunk'], List[List['Chunk']]]:
        if recipe:
            if lang != "en":
                chunker = RecursiveChunker.from_recipe(lang=lang)
            else:
                chunker = RecursiveChunker.from_recipe(recipe, lang=lang)
        else:
            chunker = RecursiveChunker(
                tokenizer_or_token_counter=tokenizer,
                chunk_size=chunk_size,
                rules=rules or RecursiveRules(),
                min_characters_per_chunk=min_characters_per_chunk
            )
        
        return Chunk._process_chunks(chunker, text)