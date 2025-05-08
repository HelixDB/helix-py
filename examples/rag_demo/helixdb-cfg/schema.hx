N::Doc {
    content: String
}
    
V::Embedding {
    chunk: String,
    vec: [F64]
}

N::Chunk {
    content: String
}

E::EmbeddingOf {
    From: Doc,
    To: Embedding, 
    Properties: {
    }
}