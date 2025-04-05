## helix-py
We're building a python library around Helix-DB to simplify building quick and easy RAG applications
to run both locally and in the cloud. The goal is to have a pytorch like front-end to creating your
custom queries. These can be both graph and vector queries for helix, but will end up being wound into
a full rag pipeline so you can spin up an llm with your documents in ~5 lines of python.

### Getting started
First install [HelixDB](https://github.com/HelixDB/helix-db). See [getting started](https://github.com/HelixDB/helix-db?tab=readme-ov-file#getting-started) in the repo.
```bash
pip install -e . # for dev
```
see `examples/`

### Roadmap
- [X] Goal 1: default data loading and http client up and running
- [ ] Goal 2: full working default queries
- [ ] Goal 3: working docs to emedding vectors relation to get docs for rag
- [ ] Goal 4: connect with a model downloaded via huggingface lib and have working rag app
- [ ] Goal 5: process docs via chunking, tokenization, and vectorization (possibly in c)

### License
helix-py is licensed under the GNU General Public License v3.0 (GPL-3.0).