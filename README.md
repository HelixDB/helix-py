## helix-py
We're building a python library around Helix-DB to simplify building quick and easy RAG applications
to run both locally and in the cloud. helix-py is meant to simply the process of feeding your private
documents into an open source llm to get the best responses for your use case.

The goal is to have a pytorch like front-end to creating your custom queries. These can be both graph
and vector queries for helix

### todo/roadmap/ideas
- goal 1: load up index, search and get vectors, insert vectors, delete vectors
- goal 2: embedding model pipeline, process docs
- goal 3: connect with a model downloaded via huggingface lib
- goal 4: fully connected via bindings in helix (option for no http)

- ex: simple run with llama3.2:1b
- ex: simple run in backend server with flask
- ex: loading data from huggingface and working with that

- comment all functions so documentation is super easy
- write tests for everything
- write all need to be fast text processing in c (tokenizer, chunker) for loader

see `main.py` for an example

### License
helix-py is licensed under the GNU General Public License v3.0 (GPL-3.0).