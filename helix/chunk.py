from chonkie import TokenChunker, SentenceChunker, RecursiveChunker, RecursiveRules, CodeChunker, SemanticChunker, LateChunker, NeuralChunker, SlumberChunker
from chonkie.genie import GeminiGenie
import requests
from pathlib import Path
from markitdown import MarkItDown
from typing import List, Optional, Union, Any, BinaryIO
from tokenizers import Tokenizer

class Chunk:
    md = MarkItDown()

    # this method helps handle the common chunking logic e.g single text or batch text
    @staticmethod
    def _process_chunks(chunker, text: Union[str, List[str]]) -> Union[List[str], List[List[str]]]:
        """
        Process text chunks using the provided chunker. Handles both single text and batch text.

        Args:
            chunker (Any): The chunker instance to use.
            text (Union[str, List[str]]): Text to chunk (single string or list of strings).

        Returns:
            Union[List[str], List[List[str]]]: List of text chunks.
        """
        list_of_chunks = []
        if isinstance(text, str):
            chonkie_chunks = chunker.chunk(text)
            for chunk in chonkie_chunks:
                list_of_chunks.append(chunk.text)
        else:
            batch_chunks = chunker.chunk_batch(text)
            for batch in batch_chunks:
                for chunk in batch:
                    list_of_chunks.append(chunk.text)

        return list_of_chunks
    
    # this is for chonkie token chunker
    @staticmethod
    def token_chunk(text: Union[str, List[str]], chunk_size: int = 2048, chunk_overlap: int = 12, tokenizer: Optional[Any] = None) -> Union[List[str], List[List[str]]]:
        """
        Chunk text by tokens with a specified chunk size and overlap.

        Args:
            text (Union[str, List[str]]): Text to chunk (single string or list of strings).
            chunk_size (int, optional): Maximum size of each chunk in tokens. Defaults to 2048.
            chunk_overlap (int, optional): Number of overlapping tokens between chunks. Defaults to 12.
            tokenizer (Optional[Any], optional): Custom tokenizer to use. Defaults to None.

        Returns:
            Union[List[str], List[List[str]]]: List of text chunks.
        """
        if tokenizer:
            custom_tokenizer = Tokenizer.from_pretrained(tokenizer)
            chunker = TokenChunker(tokenizer=custom_tokenizer, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        else:
            chunker = TokenChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        
        return Chunk._process_chunks(chunker, text)

    # this is for chonkie sentence chunker
    @staticmethod
    def sentence_chunk(text: Union[str, List[str]], tokenizer: str = "character", chunk_size: int = 2048, chunk_overlap: int = 12, min_sentences_per_chunk: int = 1) -> Union[List[str], List[List[str]]]:
        """
        Chunk text by sentences while respecting token limits.

        Args:
            text (Union[str, List[str]]): Text to chunk (single string or list of strings).
            tokenizer (str, optional): Tokenizer type to use. Defaults to "character".
            chunk_size (int, optional): Maximum size of each chunk in tokens. Defaults to 2048.
            chunk_overlap (int, optional): Number of overlapping tokens between chunks. Defaults to 12.
            min_sentences_per_chunk (int, optional): Minimum number of sentences in each chunk. Defaults to 1.

        Returns:
            Union[List[str], List[List[str]]]: List of text chunks.
        """
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
                       recipe: Optional[str] = None, lang: str = "en") -> Union[List[str], List[List[str]]]:
        """
        Chunk text using recursive rules that split on headings, paragraphs, and other structures.

        Args:
            text (Union[str, List[str]]): Text to chunk (single string or list of strings).
            tokenizer (str, optional): Tokenizer type to use. Defaults to "character".
            chunk_size (int, optional): Maximum size of each chunk in tokens. Defaults to 2048.
            rules (Optional[Any], optional): Custom recursive splitting rules. Defaults to None.
            min_characters_per_chunk (int, optional): Minimum characters per chunk. Defaults to 24.
            recipe (Optional[str], optional): Predefined chunking recipe to use. Defaults to None.
            lang (str, optional): Language code for language-specific rules. Defaults to "en".

        Returns:
            Union[List[str], List[List[str]]]: List of text chunks.
        """
        if recipe:
            if lang != "en":
                chunker = RecursiveChunker.from_recipe(recipe, lang=lang)
            else:
                chunker = RecursiveChunker.from_recipe(recipe)
        else:
            chunker = RecursiveChunker(
                tokenizer_or_token_counter=tokenizer,
                chunk_size=chunk_size,
                rules=rules or RecursiveRules(),
                min_characters_per_chunk=min_characters_per_chunk
            )
        
        return Chunk._process_chunks(chunker, text)
    
    #this is for chonkie code chunker
    @staticmethod
    def code_chunk(text: Union[str, List[str]], language: str, tokenizer: str = "character", 
                  chunk_size: int = 2048, include_nodes: bool = False) -> Union[List[str], List[List[str]]]:
        """
        Chunk source code using language-specific syntax awareness.

        Args:
            text (Union[str, List[str]]): Code text to chunk (single string or list of strings).
            language (str): Programming language of the code (required).
            tokenizer (str, optional): Tokenizer type to use. Defaults to "character".
            chunk_size (int, optional): Maximum size of each chunk in tokens. Defaults to 2048.
            include_nodes (bool, optional): Whether to include AST nodes in output. Defaults to False.

        Returns:
            Union[List[str], List[List[str]]]: List of code chunks.
        """
        chunker = CodeChunker(
            language=language,
            tokenizer_or_token_counter=tokenizer,
            chunk_size=chunk_size,
            include_nodes=include_nodes
        )
        
        return Chunk._process_chunks(chunker, text)

    # this is for chonkie semantic chunker
    @staticmethod
    def semantic_chunk(text: Union[str, List[str]], embedding_model: str = "minishlab/potion-base-8M", 
                      threshold: float = 0.8, chunk_size: int = 2048, 
                      similarity_window: int = 3, min_sentences_per_chunk: int = 1,
                      min_characters_per_sentence: int = 24, skip_window: int = 0,
                      filter_window: int = 5, filter_polyorder: int = 3, filter_tolerance: float = 0.2,
                      delim: Union[str, List[str]] = ['.', '!', '?', '\n'],
                      include_delim: Optional[str] = "prev", **embedding_kwargs) -> Union[List[str], List[List[str]]]:
        """
        Chunk text based on semantic similarity between sentences.

        Args:
            text (Union[str, List[str]]): Text to chunk (single string or list of strings).
            embedding_model (str, optional): Model to use for embeddings. Defaults to "minishlab/potion-base-8M".
            threshold (float, optional): Similarity threshold for chunking (0-1). Defaults to 0.8.
            chunk_size (int, optional): Maximum size of each chunk in tokens. Defaults to 2048.
            similarity_window (int, optional): Window size for similarity calculation. Defaults to 3.
            min_sentences_per_chunk (int, optional): Minimum sentences per chunk. Defaults to 1.
            min_characters_per_sentence (int, optional): Minimum characters per sentence. Defaults to 24.
            skip_window (int, optional): Number of groups to skip when merging similar content. Defaults to 0.
            filter_window (int, optional): Window length for Savitzky-Golay filter. Defaults to 5.
            filter_polyorder (int, optional): Polynomial order for Savitzky-Golay filter. Defaults to 3.
            filter_tolerance (float, optional): Tolerance for filter boundary detection. Defaults to 0.2.
            delim (Union[str, List[str]], optional): Sentence delimiters. Defaults to ['.', '!', '?', '\n'].
            include_delim (Optional[str], optional): How to include delimiters ("prev", "next", None). Defaults to "prev".
            **embedding_kwargs: Additional keyword arguments for the embedding model.

        Returns:
            Union[List[str], List[List[str]]]: List of semantically coherent text chunks.
        """
        chunker = SemanticChunker(
            embedding_model=embedding_model,
            threshold=threshold,
            chunk_size=chunk_size,
            similarity_window=similarity_window,
            min_sentences_per_chunk=min_sentences_per_chunk,
            min_characters_per_sentence=min_characters_per_sentence,
            skip_window=skip_window,
            filter_window=filter_window,
            filter_polyorder=filter_polyorder,
            filter_tolerance=filter_tolerance,
            delim=delim,
            include_delim=include_delim
        )
        
        return Chunk._process_chunks(chunker, text)


    # this is for chonkie late chunker
    @staticmethod
    def late_chunk(text: Union[str, List[str]], embedding_model: str = "all-MiniLM-L6-v2", 
                  chunk_size: int = 2048, rules: Optional[Any] = None, 
                  min_characters_per_chunk: int = 24,
                  recipe: Optional[str] = None, lang: str = "en") -> Union[List[str], List[List[str]]]:
        """
        Chunk text using Late chunking (combines recursive chunking with embeddings).

        Args:
            text (Union[str, List[str]]): Text to chunk (single string or list of strings).
            embedding_model (str, optional): Model to use for embeddings. Defaults to "all-MiniLM-L6-v2".
            chunk_size (int, optional): Maximum size of each chunk in tokens. Defaults to 2048.
            rules (Optional[Any], optional): Custom recursive splitting rules. Defaults to None.
            min_characters_per_chunk (int, optional): Minimum characters per chunk. Defaults to 24.
            recipe (Optional[str], optional): Predefined chunking recipe to use. Defaults to None.
            lang (str, optional): Language code for language-specific rules. Defaults to "en".

        Returns:
            Union[List[str], List[List[str]]]: List of text chunks optimized for both structure and semantics.
        """

        if recipe:
            if lang != "en":
                chunker = LateChunker.from_recipe(recipe, lang=lang)
            else:
                chunker = LateChunker.from_recipe(recipe)
        else:
            chunker = LateChunker(
                embedding_model=embedding_model,
                chunk_size=chunk_size,
                rules=rules or RecursiveRules(),
                min_characters_per_chunk=min_characters_per_chunk
            )
        
        return Chunk._process_chunks(chunker, text)
    
    # this is for chonkie neural chunker
    @staticmethod
    def neural_chunk(text: Union[str, List[str]], model: str = "mirth/chonky_modernbert_base_1", 
                    device_map: str = "cpu", min_characters_per_chunk: int = 10) -> Union[List[str], List[List[str]]]:
        """
        Chunk text using a neural network model trained specifically for text chunking.

        Args:
            text (Union[str, List[str]]): Text to chunk (single string or list of strings).
            model (str, optional): Neural chunking model to use. Defaults to "mirth/chonky_modernbert_base_1".
            device_map (str, optional): Device to run the model on ("cpu", "cuda", etc). Defaults to "cpu".
            min_characters_per_chunk (int, optional): Minimum characters per chunk. Defaults to 10.

        Returns:
            Union[List[str], List[List[str]]]: List of text chunks determined by neural model.
        """
        chunker = NeuralChunker(
            model=model,
            device_map=device_map,
            min_characters_per_chunk=min_characters_per_chunk
        )
        
        return Chunk._process_chunks(chunker, text)
    
    # this is for chonkie slumber chunker
    @staticmethod
    def slumber_chunk(text: Union[str, List[str]], genie: Optional[Any] = None, 
                     tokenizer: str = "character", chunk_size: int = 1024,
                     rules: Optional[Any] = None, candidate_size: int = 128,
                     min_characters_per_chunk: int = 24, 
                     verbose: bool = True) -> Union[List[str], List[List[str]]]:
        """
        Chunk text using LLM-guided chunking (Slumber chunker) for optimal semantic boundaries.

        Args:
            text (Union[str, List[str]]): Text to chunk (single string or list of strings).
            genie (Optional[Any], optional): LLM interface to use. Defaults to None (will use Gemini).
            tokenizer (str, optional): Tokenizer type to use. Defaults to "character".
            chunk_size (int, optional): Maximum size of each chunk in tokens. Defaults to 1024.
            rules (Optional[Any], optional): Custom recursive splitting rules. Defaults to None.
            candidate_size (int, optional): Size of candidate chunks to evaluate. Defaults to 128.
            min_characters_per_chunk (int, optional): Minimum characters per chunk. Defaults to 24.
            verbose (bool, optional): Whether to print progress information. Defaults to True.

        Returns:
            Union[List[str], List[List[str]]]: List of text chunks optimized by LLM guidance.
        """
        if genie is None:
            genie = GeminiGenie("gemini-2.5-pro-preview-03-25")
            
        chunker = SlumberChunker(
            genie=genie,
            tokenizer_or_token_counter=tokenizer,
            chunk_size=chunk_size,
            rules=rules or RecursiveRules(),
            candidate_size=candidate_size,
            min_characters_per_chunk=min_characters_per_chunk,
            verbose=verbose
        )
        
        return Chunk._process_chunks(chunker, text)
    
    @staticmethod
    def pdf_markdown(source: Union[str, requests.Response, Path, BinaryIO]) -> str:
        try:
            return Chunk.md.convert(source).text_content
        except Exception as e:
            raise RuntimeError(f"Failed to convert PDF to markdown: {e}")