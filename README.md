# helix-py
[Helix-DB](https://github.com/HelixDB/helix-db) | [Homepage](https://www.helix-db.com/) | [Documentation](https://docs.helix-db.com/introduction/overview) | [PyPi](https://pypi.org/project/helix-py/)

helix-py is a python library for interacting with [helix-db](https://github.com/HelixDB/helix-db) a
graph-vector database written in rust. With a pytorch-like query interface, it supports vector
operations and custom queries, ideal for tasks like similarity search and knowledge graph
construction. This library is meant to extend helix-db to be more easily used in machine learning
applications.

helix-py will soon be built to become a full knowledge graph framework. (this will be v0.3.0)

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

### Queries
helix-py using a pytorch like front-end to creating queries. Like you would define a neural network
forward pass, you can do the same thing for a helix-db query. We provide some default queries in
`helix/client.py` to get started with inserting and search vectors, but you can also define you're
own queries if you plan on doing more complex things. For example, for this hql query
```sql
QUERY add_user(name: String, age: I64) =>
  usr <- AddV<User>({name: name, age: age})
  RETURN usr
```
you would write
```python
from helix import Query

class add_user(Query):
    def __init__(self, name: str, age: int):
        super().__init__()
        self.name = name
        self.age = age

    def query(self) -> List[Any]:
        return [{ "name": self.name, "age": self.age }]

    def response(self, response):
        return response.get("res")
```
for your python script. Make sure that the Query.query method returns a list of objects.

### Client
To setup a simple `Client` to interface with a running helix instance:
```python
import helix
from helix.client import hnswinsert, hnswsearch

db = helix.Client(local=True, verbose=True)
data = helix.Loader("path/to/data", cols=["vecs"])
[db.query(hnswinsert(d)) for d in data] # build hnsw index

my_query = [0.32, ..., -1.321]
nearest = db.query(hnswsearch(my_query)) # query hnsw index
```

If you don't want to define a class/methods for every query you have, you can also simply
use
```python
db.query("add_user", { "name", "John", "age": 34 })
```

### Instance
To setup a simple `Instance` that automatically starts and stops a helix instance with respect
to the lifetime of the program, to interface with a `helixdb-cfg` directory you have:
```python
from helix.instance import Instance
helix_instance = Instance("helixdb-cfg", 6969, verbose=True)
```
and from there you can interact with it like you would with the `Client`

### Providers
We also provide an ollama interface. This will be expanded to include many other providers in the future.
```python
from helix.providers import OllamaClient, OpenAIClient
ollama_client = OllamaClient(use_history=True, model="mistral:latest")
# or
openai_client = OpenAIClient(use_history=False, model="gpt-4o")

while True:
    prompt = input(">>> ")
    res = ollama_client.request(prompt, stream=True)
```

### MCP
Helix's custom mcp server backend is built into the db and the `mcp_server.py` server can be used
to interface with that. To get started with this, you can for example use uv:

```bash
uv init project
cp mcp_server.py project
cd project
uv venv && source .venv/bin/activate
uv add helix-py "mcp[cli]"
```
then for claude-desktop, for example, add this to
`~/Library/Application Support/Claude/claude_desktop_config.json` adjusting paths of course
```json
{
  "mcpServers": {
    "helix-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/user/helix-py/project",
        "run",
        "mcp_server.py"
      ]
    }
  }
}
```

### Loader
The loader (`helix/loader.py`) currently supports `.parquet`, `.fvecs`, and `.csv` data. Simply pass in the path to your
file or files and the columns you want to process and the loader does the rest for you and is easy to integrate with
your queries

## License
helix-py is licensed under the The AGPL (Affero General Public License).

