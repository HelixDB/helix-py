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
- [ ] goal 2: full working default queries
- [ ] goal 3: working docs to emedding vectors relation to get docs for rag
- [ ] goal 4: connect with a model downloaded via huggingface lib and have working rag app
- [ ] goal 5: process docs via chunking, tokenization, and vectorization
    - possibly use c for chunking and tokenization (for speed)

### License
helix-py is licensed under the GNU General Public License v3.0 (GPL-3.0).