// Start writing your queries here.
//
// You can use the schema to help you write your queries.
//
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

QUERY hnswinsert(vector: [F64]) =>
    AddV<Embedding>(vector)
    RETURN "Success"

//QUERY hnswload(vectors: [[F64]]) =>
//    FOR vec IN vectors {
//        AddV<Embedding>(vec)
//    }
//    RETURN "Success"

QUERY hnswsearch(query: [F64], k: I32) =>
    res <- SearchV<Embedding>(query, k)
    RETURN res
