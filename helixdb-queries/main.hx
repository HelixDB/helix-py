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
//    RETURN res::{ID}
//
//QUERY hnswload(vectors: [[F64]]) =>
//    res <- BatchAddV<Type>(vectors)
//    RETURN res::{ID}
//
//QUERY hnswsearch(query: [F64], k: I32) =>
//    res <- SearchV<Type>(query, k)
//    RETURN res

QUERY ragloaddocs(docs: [{ doc: String, vecs: [[F64]] }]) =>
    FOR {doc, vec} IN docs {
        doc_node <- AddN<Type>({ content: doc })
        vectors <- BatchAddV<Doc>(vecs)
        FOR vec IN vectors {
            AddE<Contains>::From(doc_node)::To(vec)
        }
    }
    RETURN "Success"

//QUERY ragtestload(doc: String, vec: [F64]) =>
//    doc_node <- AddN<Type>({ content: doc })
//    vectors <- AddV<Doc>(vecs)
//    AddE<Contains>::From(doc_node)::To(vec)
//    RETURN "Success"

QUERY ragsearchdocs(query: [F64], k: I32) =>
    vec <- SearchV<Vector>(query, k)
    doc_node <- vec::In<Contains>
    RETURN doc_node::{content}