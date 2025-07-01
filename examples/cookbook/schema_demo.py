from helix import Schema

schema = Schema()

print("\nSchema:")
original_schema = schema.show_schema()

node_types = list(schema.get_nodes().keys())
edge_types = list(schema.get_edges().keys())

print("Extracted elements:")
print("Nodes:", node_types)
print("Edges:", edge_types)

# Delete all elements from schema
schema.delete_nodes(node_types)
schema.delete_edges(edge_types)

# Create the exact same schema
# Create User node type
schema.create_node(
    "User", 
    {
        "name": "String",
        "age": "U32",
        "email": "String",
        "created_at": "I32",
        "updated_at": "I32"
    }
)

# Create Post node type
schema.create_node(
    "Post", 
    {
        "content": "String",
        "created_at": "I32",
        "updated_at": "I32"
    }
)

# Create Follows edge type (User -> User)
schema.create_edge(
    "Follows", 
    "User", 
    "User", 
    {
        "since": "I32"
    }
)

# Create Created edge type (User -> Post)
schema.create_edge(
    "Created", 
    "User", 
    "Post", 
    {
        "created_at": "I32"
    }
)

print("\nRecreated schema:")
recreated_schema = schema.show_schema()

# Verify the schema was created correctly
node_types = list(schema.get_nodes().keys())
edge_types = list(schema.get_edges().keys())
print("\nVerification:")
print("Nodes:", sorted(node_types))
print("Edges:", sorted(edge_types))

print("\nVerify schemas have exact same content:")
if original_schema == recreated_schema:
    print("Schemas have exact same content")
else:
    print("Schemas do not have exact same content")

schema.save()