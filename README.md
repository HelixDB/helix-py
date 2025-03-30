## helix-py
We're building a python library around Helix-DB to simplify building quick and easy RAG applications
to run both locally and in the cloud. The goal is to have a pytorch like front-end to creating your
custom queries. These can be both graph and vector queries for helix, but will end up being wound into
a full rag pipeline so you can spin up an llm with your documents in ~5 lines of python.

### Getting started
```bash
$ python -m pip install -e . # for dev
```
see `examples/`

### License
helix-py is licensed under the GNU General Public License v3.0 (GPL-3.0).