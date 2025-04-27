# idea is a bunch of chunking methods

# types of chunking
# - simply based on a fixed chunk size of words
# - based on full sentences and a chunk size (default 200, 1 word ~= 1.3 tokens)
#   should vectorize at most 512 tokens at once with bert-base
# - based on semantic similarity, so make new chunk once the topic changes or similar
# - based on document tags like in an html doc
# - agentic style using an llm to seperate texts into chunked paragraphs based on meaning

from abc import ABC, abstractmethod
from typing import List

class Chunker(ABC):
    @abstractmethod
    def chunk(self, text: str) -> List[str]: pass

class FixedWordChunker(Chunker):
    def __init__(self, chunk_size: int=200):
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> List[str]:
        words = text.split()
        return [' '.join(words[i:i + self.chunk_size]) for i in range(0, len(words), self.chunk_size)]

class SentenceChunker(Chunker):
    def __init__(self, max_words: int=250):
        self.max_words = max_words

    def chunk(self, text: str) -> List[str]:
        pass

def chunker(method: str, **kwargs) -> Chunker:
    if method == 'fixed_word':
        return FixedWordChunker(**kwargs)
    elif method == 'sentence':
        return SentenceChunker(**kwargs)
    else:
        raise ValueError(f"Unknown chunking method: {method}")

# example usage:
#   text = "hello world"
#   chunker = chunker('fixed_word')
#   chunks = chunker.chunk(text)