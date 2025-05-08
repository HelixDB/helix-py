QUERY ragloaddocs(docs: [{ doc: String, vectors: [{vec: [F64], chunk: String}] }]) =>
    FOR {doc, vectors} IN docs {
        doc_node <- AddN<Doc>({ content: doc })
        FOR {vec, chunk} IN vectors {
            vec <- AddV<Embedding>(vec)
            chunk_node <- AddN<Chunk>({ content: chunk })
            AddE<Contains>::From(doc_node)::To(chunk_node)
            AddE<EmbeddingOf>::From(chunk_node)::To(vec)
        }
    }
    RETURN "Success"

QUERY ragsearchdocs(query: [F64], k: I32) =>
    vec <- SearchV<Embedding>(query, k)
    chunks <- vec::In<EmbeddingOf>
    RETURN chunks::{content}
