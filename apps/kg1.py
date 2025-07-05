#!/usr/bin/env python3
from helix import Hnode, Hedge, json_to_helix
from helix.providers import OpenAIClient
import helix
from typing import List
from chonkie import RecursiveRules, RecursiveLevel, RecursiveChunker, SemanticChunker
import pymupdf4llm
import argparse
import json
import time

llm_client = OpenAIClient(model="gpt-4o")
# helix.Instance here
db_client = helix.Client(local=True)

class insert_entity(helix.Query):
    def __init__(self, entity_name: str):
        super().__init__()
        self.entity_name = entity_name

    def query(self):
        #exists = db_client.query(get_entity(self.entity_name))
        #if not exists:
        return [{ "entity_name_in": self.entity_name }]
        #else:
        #    return []

    def response(self, response):
        return response

class get_entity(helix.Query):
    def __init__(self, entity_name: str):
        super().__init__()
        self.entity_name = entity_name

    def query(self):
        return [{ "entity_name_in": self.entity_name }]

    def response(self, response):
        return response.get("node")

class insert_relationship(helix.Query):
    def __init__(self, from_entity_label: str, to_entity_label: str, edge_name: str):
        super().__init__()
        self.from_entity_label = from_entity_label
        self.to_entity_label = to_entity_label
        self.edge_name = edge_name

    def query(self):
        return [{
            "from_entity_label": self.from_entity_label,
            "to_entity_label": self.to_entity_label,
            "edge_name_in": self.edge_name
        }]

    def response(self, response):
        return response

class get_ne(helix.Query):
    def __init__(self): super().__init__()
    def query(self): return [{}]
    def response(self, response): return json.loads(response)

def insert_e_r(nodes: List[Hnode], edges: List[Hedge]):
    for node in nodes:
        db_client.query(insert_entity(node.label))

    for edge in edges:
        db_client.query(insert_relationship(
            str(edge.from_node_label),
            str(edge.to_node_label),
            str(edge.label),
        ))

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

def gen_n_and_e(chunks: str):
    prompt = """You are task is to only produce json structured output and nothing else. Do no
        provide any extra commentary or text. Based on the following sentence/s, split it into
        node entities and edge connections. Only create nodes based on people, locations,
        objects, concepts, events, and attributes and edges based on adjectives and verbs
        related to those nodes. Don't put the json in markdown tags either.
        Avoid at allcosts, classifying any useless/fluff parts in the
        chunk of text. If you deem parts of a text as not relevent or opinionated, do not create
        nodes or edges for it. Limit the amount of nodes and edges you create. Here is an example
        of what you should produce:
        {
            "Nodes": [
                {
                  "Label": "marie curie"
                }
            ],
            "Edges": [
                {
                  "Label": "wife",
                  "Source": "alice curie",
                  "Target": "pierre curie"
                }
            ]
        }
        Now do this on this text:
    """
    ret = []
    for chunk in chunks:
        res = llm_client.request(prompt + chunk)
        ret.append(res)
        print(res)
    return ret

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
        Marie Curie, born on 7 November 1867 in Warsaw, Poland, was a brilliant physicist and chemist whose curiosity and perseverance changed the course of science. From a young age, Marie displayed an insatiable hunger for knowledge. Despite the limitations placed on women in education at the time, she pursued her studies with determination, eventually moving to Paris to attend the Sorbonne. There, she immersed herself in physics and mathematics, often studying late into the night, sustained only by her passion and the occasional crust of bread.
        It was at the Sorbonne that she met Pierre Curie, a quiet but brilliant physicist with whom she would form both a romantic and scientific partnership. Their shared fascination with the invisible forces of nature—particularly magnetism and radioactivity—brought them together. They married in 1895 and began working side by side in a makeshift laboratory, often in difficult and even dangerous conditions. In 1903, their tireless efforts led to the discovery of two new radioactive elements, polonium and radium, earning them, along with Henri Becquerel, the Nobel Prize in Physics. It was the first Nobel ever awarded to a woman.
        Tragedy struck in 1906 when Pierre was killed in a street accident. Grief-stricken but resolute, Marie took over his teaching position, becoming the first female professor at the University of Paris. She continued their work on radioactivity, eventually isolating radium in its pure form. Her pioneering research earned her a second Nobel Prize in 1911—this time in Chemistry—making her the first person to win Nobel Prizes in two different scientific fields. Her legacy of scientific excellence would continue through her children and grandchildren, with the Curie family ultimately earning five Nobel Prizes.
        And then, there was Robin Williams. A century later, in a very different field, his contagious energy and quicksilver wit lit up the world in a way that echoes Marie Curie's radiance—figuratively speaking. Though their lives couldn’t have been more different, Williams once joked during a stand-up set that Marie Curie must have been "the original glow stick," unknowingly blending comedy with an obscure nod to science. It’s easy to imagine that, had their paths somehow crossed across time and space, Robin would have found a way to make Marie laugh, while she would have quietly corrected his terminology—before handing him a lead apron, just in case.
    """

    md_text = convert_to_markdown(in_doc, doc_type)
    chunked_text = chunker(sample_text, chunking_method)
    gened = gen_n_and_e(chunked_text[:3])
    l_nodes_edges = [json_to_helix(gen) for gen in gened]
    for nodes, edges in l_nodes_edges:
        print(nodes, edges)
        insert_e_r(nodes, edges)

