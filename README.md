# helix-py
[Helix-DB](https://github.com/HelixDB/helix-db) | [Homepage](https://www.helix-db.com/) | [Documentation](https://docs.helix-db.com/introduction/overview) | [PyPi](https://pypi.org/project/helix-py/)

helix-py is a Python library for interacting with [helix-db](https://github.com/HelixDB/helix-db) a
powerful graph-vector database written in Rust. It provides both a simple query interface and a PyTorch-like
front-end for defining and executing custom graph queries and vector-based operations. This makes it
well-suited for use cases such as similarity search, knowledge graph construction, and machine learning pipelines.

## Installation

### Install helix-py
`uv add helix-py` or `pip install helix-py`

See [getting started](https://github.com/HelixDB/helix-db?tab=readme-ov-file#getting-started) for more
information on installing helix-db

### Install the Helix CLI
```bash
curl -sSL "https://install.helix-db.com" | bash
helix install
```

## Features

### Client
To setup a simple `Client` to interface with a running helix instance:
```python
import helix

db = helix.Client(local=True, verbose=True)

db.query('add_user', {"name": "John", "age": 20})
```
The default port is `6969`, but you can change it by passing in the `port` parameter.
For cloud instances, you can pass in the `api_endpoint` parameter.

### Queries
helix-py allows users to define a PyTorch-like manner, similar to how
you would define a neural network's forward pass. You can use built-in queries in `helix/client.py`
to get started with inserting and search vectors, or you can define your own queries for more complex workflows.

**Pytorch-like Query**

```rust
QUERY add_user(name: String, age: I64) =>
  usr <- AddV<User>({name: name, age: age})
  RETURN usr
```
You can define a matching Python class:
```python
from helix import Query
from helix.types import Payload

class add_user(Query):
    def __init__(self, name: str, age: int):
        super().__init__()
        self.name = name
        self.age = age

    def query(self) -> Payload:
        return [{ "name": self.name, "age": self.age }]

    def response(self, response):
        return response

db.query(add_user("John", 20))
```

Make sure that the `Query.query` method returns a list of objects.

### Instance
To setup a simple `Instance` that automatically starts and stops a helix instance with respect
to the lifetime of the program, to interface with a `helixdb-cfg` directory you have:
```python
from helix.instance import Instance
helix_instance = Instance("helixdb-cfg", 6969, verbose=True)
```
> `helixdb-cfg` is the directory where the configuration files are stored.

and from there you can interact with the instance using `Client`.

The instance will be automatically stopped when the script exits.

### Providers
Helix has LLM interfaces for popular LLM providers. 

Available providers:
- `OpenAIProvider`
- `GeminiProvider`
- `AnthropicProvider`

All providers expose two methods:
- `enable_mcps(name: str, url: str=...) -> bool` to enable Helix MCP tools
- `generate(messages, response_model: BaseModel | None=None) -> str | BaseModel`

The generate method supports messages in the 2 formats:
- **Free-form text**: pass a string
- **Message lists**: pass a list of `dict` or provider-specific `Message` models

It also supports structured outputs by passing a Pydantic model to get validated results.

Examples (see `examples/llm_providers/providers.ipynb` for full demos):
```python
from pydantic import BaseModel

# OpenAI
from helix.providers.openai_client import OpenAIProvider
openai_llm = OpenAIProvider(
    name="openai-llm",
    instructions="You are a helpful assistant.",
    model="gpt-5-nano",
    history=True
)
print(openai_llm.generate("Hello!"))

class Person(BaseModel):
    name: str
    age: int
    occupation: str

print(openai_llm.generate([{"role": "user", "content": "Who am I?"}], Person))
```

To enable MCP tools with a running Helix MCP server (see [MCP section](#mcp)):
```python
openai_llm.enable_mcps("helix-mcp")         # uses default http://localhost:8000/mcp/
gemini_llm.enable_mcps("helix-mcp")         # uses default http://localhost:8000/mcp/
anthropic_llm.enable_mcps("helix-mcp", url="https://your-remote-mcp/...")
```

Notes:
- OpenAI GPT-5 family models support reasoning while other models use temperature.
- Anthropic local streamable MCP is not supported; use a URL-based MCP.

### Embedders
Helix has embedder interfaces for popular embedding providers.

Available embedders:
- `OpenAIEmbedder`
- `GeminiEmbedder`
- `VoyageAIEmbedder`

Each embedder implements:
- `embed(text: str, **kwargs)` returns a vector `[F64]`
- `embed_batch(texts: List[str], **kwargs)` returns a list of vectors `[F64]`

Examples (see `examples/llm_providers/providers.ipynb` for more):
```python
from helix.embedding.openai_client import OpenAIEmbedder
openai_embedder = OpenAIEmbedder()  # requires OPENAI_API_KEY
vec = openai_embedder.embed("Hello world")
batch = openai_embedder.embed_batch(["a", "b", "c"])

from helix.embedding.gemini_client import GeminiEmbedder
gemini_embedder = GeminiEmbedder()
vec = gemini_embedder.embed("doc text", task_type="RETRIEVAL_DOCUMENT")

from helix.embedding.voyageai_client import VoyageAIEmbedder
voyage_embedder = VoyageAIEmbedder()
vec = voyage_embedder.embed("query text", input_type="query")
```

### MCP
Helix includes a ready-to-run MCP server exposing graph traversal and search tools from your helix instance.

Key classes are in `helix/mcp.py`:
- `MCPServer(name, client, tool_config=ToolConfig(), embedder=None, embedder_args={})`
- `ToolConfig` to enable/disable tools (e.g., `search_vector`, `search_vector_text`, `search_keyword`, traversal tools)

Starting a server (simple):
```python
# examples/mcp_server.py
from helix.client import Client
from helix.mcp import MCPServer, ToolConfig
from helix.embedding.openai_client import OpenAIEmbedder

helix_client = Client(local=True)
openai_embedder = OpenAIEmbedder()  # needs OPENAI_API_KEY
mcp_server = MCPServer("helix-mcp", helix_client, tool_config=tool_config, embedder=openai_embedder)
mcp_server.run()  # streamable-http on http://127.0.0.1:8000/mcp/
```

Alternative app entry (with explicit host/port):
```python
# apps/mcp_server.py
from helix.client import Client
from helix.mcp import MCPServer
from helix.embedding.openai_client import OpenAIEmbedder

client = Client(local=True, port=6969)
openai_embedder = OpenAIEmbedder()
mcp_server = MCPServer("helix-mcp", client, embedder=openai_embedder)

if __name__ == "__main__":
    mcp_server.run(transport="streamable-http", host="127.0.0.1", port=8000)
```

Configure Claude Desktop to use the local MCP server (adjust paths):
```json
{
  "mcpServers": {
    "helix-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/your/app/folder",
        "run",
        "mcp_server.py"
      ]
    }
  }
}
```

Environment variables:
- `OPENAI_API_KEY`, `GEMINI_API_KEY`, `VOYAGEAI_API_KEY`, `ANTHROPIC_API_KEY` as needed.

MCP tools overview (enabled via `ToolConfig`):
- Traversal: `n_from_type`, `e_from_type`, `out_step`, `out_e_step`, `in_step`, `in_e_step`, `filter_items`
- Search: `search_vector` (requires `embedder`), `search_vector_text` (server-side embedding), `search_keyword`

### Schema
To dynamically create, load, and edit your Helixdb schema, you can use the `Schema` class.
To get started, you can create a `schema` instance and optionally pass in the path to your configs file.
```python
from helix.loader import Schema
schema = Schema()
```

This will either create a new `schema.hx` file if you don't have one, or load the existing one.

To interact with the schema, you can use various methods, including:
```python
schema.create_node("User", {"name": "String", "age": "U32"})
schema.create_edge("Follows", "User", "User")
schema.create_vector("Vec", {"vec": "Vec32"})
```

To save the schema to your configs folder, you can use the `save` method.
```python
schema.save()
```

### Chunking

Helix uses [Chonkie](https://chonkie.ai/) chunking methods to split text into manageable pieces for processing and embedding:

```python
from helix import Chunk

text = "Your long document text here..."
chunks = Chunk.token_chunk(text)

semantic_chunks = Chunk.semantic_chunk(text)

code_text = "def hello(): print('world')"
code_chunks = Chunk.code_chunk(code_text, language="python")

texts = ["Document 1...", "Document 2...", "Document 3..."]
batch_chunks = Chunk.sentence_chunk(texts)
```

You can find all the different chunking examples inside of [the documentation](https://docs.helix-db.com/features/chunking/helix-chunking).

## Loader
The loader (`helix/loader.py`) currently supports `.parquet`, `.fvecs`, and `.csv` data. Simply pass in the path to your
file or files and the columns you want to process and the loader does the rest for you and is easy to integrate with
your queries

## License
helix-py is licensed under the The AGPL (Affero General Public License).

