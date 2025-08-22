import helix

massive_text_blob = """
This is a massive text blob that we want to chunk into smaller pieces for processing. 
It contains multiple sentences and paragraphs that need to be divided appropriately 
to maintain context while fitting within token limits. The chunker should handle 
overlaps properly to ensure no important information is lost at chunk boundaries. 
This example demonstrates how the token chunker works with a realistic text sample 
that would be common in document processing and RAG applications. The chunks will 
be created with specified token limits and overlap settings to optimize for both 
comprehension and processing efficiency. Each chunk will contain metadata about 
its position in the original text and token count for further processing.
"""

########### Token Chunker ############

# Single Text Chunking
chunks = helix.Chunk.token_chunk(massive_text_blob, chunk_size=100, chunk_overlap=10)

print(f"Created {len(chunks)} chunks:")
for i, chunk in enumerate(chunks):
    print(f"\nChunk {i+1}:")
    print(f"  Text: {chunk.text}")
    print(f"  Start: {chunk.start_index}")
    print(f"  End: {chunk.end_index}")
    print(f"  Tokens: {chunk.token_count}")

# Batch Chunking for Token Chunker

texts = [
    "First document to chunk with some content for testing.",
    "Second document with different content for batch processing."
]

batch_chunks = helix.Chunk.token_chunk(texts, chunk_size=50, chunk_overlap=5)

for doc_idx, doc_chunks in enumerate(batch_chunks):
    print(f"\nDocument {doc_idx + 1} ({len(doc_chunks)} chunks):")
    for chunk_idx, chunk in enumerate(doc_chunks):
        print(f"  Chunk {chunk_idx + 1}: {chunk.text} (tokens: {chunk.token_count})")


########### Token Chunker ############