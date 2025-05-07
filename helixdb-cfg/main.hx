// Start writing your queries here.
//
// You can use the schema to help you write your queries.  //
// Queries take the form:
//     QUERY {query name}({input name}: {input type}) =>
//         {variable} <- {traversal}
//         RETURN {variable}
//
// Example:
//     QUERY GetUserFriends(user_id: String) =>
//         friends <- N<User>(user_id)::Out<Knows>
//         RETURN friends
//
//
// For more information on how to write queries,
// see the documentation at https://docs.helix-db.com
// or checkout our GitHub at https://github.com/HelixDB/helix-db

//QUERY hnswinsert(vector: [F64]) =>
//    res <- AddV<Vector>(vector)
//    RETURN res
//
//QUERY hnswload(vectors: [[F64]]) =>
//    res <- BatchAddV<Vector>(vectors)
//    RETURN res
//
//QUERY hnswsearch(query: [F64], k: I32) =>
//    res <- SearchV<Vector>(query, k)
//    RETURN res

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