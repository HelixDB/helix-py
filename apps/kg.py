#!/usr/bin/env python3
from helix import Hnode, Hedge, json_to_helix
from helix.providers import OllamaClient
import helix
from chonkie import RecursiveRules, RecursiveLevel, RecursiveChunker, SemanticChunker
import pymupdf4llm
import argparse

ollama_client = OllamaClient(use_history=True, model="mistral:latest")

class insert_entity(helix.Query):
    def __init__(self, label: str):
        super().__init__()
        self.label = label
    def query(self): return [{ "label": self.label }]
    def response(self, response): return response

class get_entity(helix.Query):
    def __init__(self, label: str):
        super().__init__()
        self.label = label
    def query(self): return [{ "label": self.label }]
    def response(self, response): return response

class insert_relationship(helix.Query):
    def __init__(self, from_entity_label: str, to_entity_label: str, label: str):
        super().__init__()
        self.from_entity_label = from_entity_label
        self.to_entity_label = to_entity_label
        self.label = label
    def query(self): return [{
        "from_entity_label": self.from_entity_label,
        "to_entity_label": self.to_entity_label,
        "label": self.label
    }]
    def response(self, response): return response

# func: go through list of nodes and edges to send them to helix
#   func: some sort of simple way to check if a node already exists

def chunker(text: str, chunk_style: str="recursive", chunk_size: int=100):
    chunked_text = ""
    match chunk_style.lower():
        case "recursive":
            rules = RecursiveRules(
                    levels=[
                        RecursiveLevel(delimiters=['######', '#####', '####', '###', '##', '#']),
                        RecursiveLevel(delimiters=['\n\n', '\n', '\r\n', '\r']),
                        RecursiveLevel(delimiters='.?!;:'),
                        RecursiveLevel()
                        ]
                    )
            chunker = RecursiveChunker(rules=rules, chunk_size=chunk_size)
            chunked_text = chunker(text)

        case "semantic":
            chunker = SemanticChunker(
                    embedding_model="minishlab/potion-base-8M",
                    threshold="auto",
                    chunk_size=chunk_size,
                    min_sentences=1
            )
            chunked_text = chunker(text)

        case _:
            raise RuntimeError("unknown chunking style")

    [print(c, "\n--------\n") for c in chunked_text]
    return [c.text for c in chunked_text]

def convert_to_markdown(path: str, doc_type: str) -> str:
    if doc_type not in ["pdf", "csv"]:
        raise RuntimeError("unknown doc type")

    md_convert = None
    if path.endswith(".pdf") and doc_type == "pdf":
        md_convert = pymupdf4llm.to_markdown(path)
    return str(md_convert)

# TODO: future would be cool with some sort of tool call
def gen_n_and_e(chunks: str):
    prompt = """You are task is to only produce json structured output and nothing else. Do no
        provide any extra commentary or text. Based on the following sentence/s, split it into
        node entities and edge connections. Only create nodes based on people, locations,
        objects, concepts, events, and attributes and edges based on adjectives and verbs
        related to those nodes. Avoid at allcosts, classifying any useless/fluff parts in the
        chunk of text. If you deem parts of a text as not relevent or opinionated, do not create
        nodes or edges for it. Limit the amount of nodes and edges you create. Here is an example
        of what you should produce:
        {
            "Nodes": [
                {
                  "Label": "Marie Curie"
                }
            ],
            "Edges": [
                {
                  "Label": "Wife",
                  "Source": "Alice Curie",
                  "Target": "Pierre Curie"
                }
            ]
        }
        Now do this on this text:
    """
    return [ollama_client.request(prompt + chunk) for chunk in chunks]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="helix knowledge workflow")
    parser.add_argument("input", help="input file path", nargs=1)
    parser.add_argument("-t", "--type", help="input doc type (pdf, ...)", default="pdf")
    parser.add_argument("-c", "--chunking_method", help="chunking method (recursive, semantic", default="recursive")
    args = parser.parse_args()

    in_doc = args.input[0]
    doc_type = args.type
    chunking_method = args.chunking_method

    # testing
    sample_text = """
        Marie Curie, 7 November 1867 – 4 July 1934, was a Polish and naturalised-French physicist and chemist who conducted pioneering research on radioactivity.
        She was the first woman to win a Nobel Prize, the first person to win a Nobel Prize twice, and the only person to win a Nobel Prize in two scientific fields.
        Her husband, Pierre Curie, was a co-winner of her first Nobel Prize, making them the first-ever married couple to win the Nobel Prize and launching the Curie family legacy of five Nobel Prizes.
        She was, in 1906, the first woman to become a professor at the University of Paris.
        Also, Robin Williams.
    """

    db = helix.Client(local=True)
    res = db.query(insert_entity("poop"))
    print(res)
    res = db.query(get_entity("poop"))
    print(res)

    exit(1)

    md_text = convert_to_markdown(in_doc, doc_type)
    chunked_text = chunker(sample_text, chunking_method)
    gened = gen_n_and_e(chunked_text[:3])
    l_nodes_edges = [json_to_helix(gen) for gen in gened]
    for nodes, edges in l_nodes_edges:
        print(nodes, edges)

    #while True:
    #    prompt = input(">>> ")
    #    res = ollama_client.request(prompt, stream=True)

"""
[
    Hnode(label=Marie Curie, id=None, properties=None),
    Hnode(label=Physicist, id=None, properties=None),
    Hnode(label=Chemist, id=None, properties=None),
    Hnode(label=Nobel Prize Winner, id=None, properties=None),
    Hnode(label=First Woman to Win a Nobel Prize, id=None, properties=None),
    Hnode(label=First Person to Win a Nobel Prize Twice, id=None, properties=None),
    Hnode(label=Only Person to Win a Nobel Prize in Two Scientific Fields, id=None, properties=None)
]
[
    Hedge(label=Is, from=Marie Curie, to=Physicist, type=EdgeType.Node, id=None, properties=None),
    Hedge(label=Is, from=Marie Curie, to=Chemist, type=EdgeType.Node, id=None, properties=None)
]

[
    Hnode(label=Marie Curie, id=None, properties=None),
    Hnode(label=Pierre Curie, id=None, properties=None),
    Hnode(label=University of Paris, id=None, properties=None),
    Hnode(label=Robin Williams, id=None, properties=None)
]
[
    Hedge(label=Held Position at, from=Marie Curie, to=University of Paris, type=EdgeType.Node, id=None, properties=None)
]
"""

