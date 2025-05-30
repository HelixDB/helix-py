# helix-py
[Helix-DB](https://github.com/HelixDB/helix-db) | [Homepage](https://www.helix-db.com/) | [Documentation](https://docs.helix-db.com/introduction/overview) | [PyPi](https://pypi.org/project/helix-py/)

Helix-py is a python library for interacting with [helix-db](https://github.com/HelixDB/helix-db) a
graph-vector database written in rust.
This library will make it easy to quickly setup a rag agent with your documents and favorite model.

## Features

### Queries
helix-py using a pytorch like front-end to creating queries. Like you would define a neural network
forward pass, you can do the same thing for a helix-db query. We provide some default queries in
`helix/client.py` to get started with inserting and search vectors, but you can also define you're
own queries if you plan on doing more complex things. For example, for this hql query
```sql
QUERY addUser(name: String, age: Integer) =>
  AddV<User>({name: name, nge: age})
  RETURN "Success"
```
you would write
```python
class addUser(Query):
    def __init__(self, user: Tuple[str, int]):
        super().__init__()
        self.user = user
    def query(self) -> List[Any]:
        return [{ "name": self.user[0], "age": self.user[1] }]
    def response(self, response):
        pass
```
for your python script. Make sure that the Query.query method returns a list of objects.

### Loader
The loader (`helix/loader.py`) currently supports `.parquet`, `.fvecs`, and `.csv` data. Simply pass in the path to your
file or files and the columns you want to process and the loader does the rest for you and is easy to integrate with
your queries

## Installation
### Install helix-py
```bash
pip install helix-py
```
See [getting started](https://github.com/HelixDB/helix-db?tab=readme-ov-file#getting-started) for more
information on installing helix-db

### Install the Helix CLI
```bash
curl -sSL "https://install.helix-db.com" | bash
helix install
helix init
helix deploy
```

### Install Ollama
Install [Ollama here](https://ollama.com/download)

Then run ollama and the model you want to use
```bash
ollama serve
ollama run llama3.1:8b
```


Now you're good to go! See `examples/` for how to use helix-py. See
`helixdb-queries/queries.hx` for the queries installed with `helix deploy --local`. You can add your own here
and write corresponding `Query` classes in your python script.

## Documentation
Proper docs are coming soon. See `examples/tutorial.py` for now.
```python
import helix
from helix.client import hnswload, hnswsearch

db = helix.Client(local=True)
data = helix.Loader("path/to/data", cols=["vecs"])
ids = db.query(hnswload(data)) # build hnsw index

my_query = [0.32, ..., -1.321]
nearest = db.query(hnswsearch(my_query)) # query hnsw index
```

## Roadmap
- [X] Goal 1: default data loading and http client up and running
- [X] Goal 2: full working default queries
- [X] Goal 3: working rag pipeline with default queries and workflow
- [ ] Goal 4: processing, chunking, tokenizing, vectorising data
- [ ] Goal 5: some sort of knowledge storing and loading system to build a brain for an llm (for now)

## License
helix-py is licensed under the GNU General Public License v3.0 (GPL-3.0).
