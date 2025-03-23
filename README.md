### helixdb-py
We're building a python library around Helix-DB to simplify building quick and easy RAG applications
to run both locally and in the cloud. HelixDB-Py is meant to simply the process of feeding your private
documents into an open source llm to get the best responses for your use case.

#### todo/roadmap
- goal 1: simply load index, search and get vectors, insert vectors, delete vectors
- goal 2: embedding model pipeline, process docs
- goal 3: connect with a model downloaded via huggingface lib

- what a helixdb-py script should look like (pseudo):
```python
import helixdb
docs = Loader('path to documents dir')
index = HNSW(docs)

import huggingface
model = huggingface.import('llama3.2:1b')

rag = RAG(model, docs)

prompt()
```

need a way to:
- talk to helix-db, most likely via an http connection
- llm responses -> embedding -> search -> feed into llm response

#### License
HelixDB-Py is licensed under the GNU General Public License v3.0 (GPL-3.0).