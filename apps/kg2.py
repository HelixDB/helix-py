#!/usr/bin/env python3
from helix import Hnode, Hedge, json_to_helix
import helix
from typing import List
from chonkie import RecursiveRules, RecursiveLevel, RecursiveChunker, SemanticChunker
import pymupdf4llm
import json
import spacy
import argparse
from tqdm import tqdm

db_client = helix.Client(local=True, verbose=True)
nlp = spacy.load("en_core_web_sm")

def insert_e_r(chunk_vec: str, nodes: List[Hnode], edges: List[Hedge]):
    vec_id = db_client.query("insert_vec_chunk", {
        "chunk": chunk_vec
    })[0]["vec"]["id"]

    for node in tqdm(nodes, desc="inserting nodes"):
        # this is a very basic way of deduplicating
        node_ret = db_client.query("get_entity", {"entity_name_in": node.label.lower()})[0]["node"]
        if not node_ret: db_client.query("insert_entity", {
            "entity_name_in": node.label.lower(),
            "chunk_vec_id": vec_id,
        })

    for edge in tqdm(edges, desc="inserting edges"):
        db_client.query("insert_relationship", {
            "from_entity_label": edge.from_node_label.lower(),
            "to_entity_label": edge.to_node_label.lower(),
            "edge_name_in": edge.label.lower(),
        })

def chunker(text: str, chunk_style: str="recursive", chunk_size: int=150):
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

def gen_ne(doc) -> List:
    relationships = []
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "NORP", "GPE", "PRODUCT", "ORG", "EVENT", "WORK_OF_ART"]:
            entity_text = ent.text
            # check nearby tokens (±3 tokens) for descriptive terms
            for token in doc[max(0, ent.start - 3):ent.end + 3]:
                if token.pos_ in ("ADJ", "NOUN") and \
                   token.text not in entity_text and \
                   token.text.lower() not in ("was", "the", "a", "and", "in", "of", "to", "on", "first", "couple", "co-winner"):
                    # ensure token isn't part of an unrelated entity
                    if not any(e.start <= token.i <= e.end and e.label_ not in ("PERSON", "NORP", "GPE", "PRODUCT", "ORG", "EVENT", "WORK_OF_ART") for e in doc.ents):
                        # check for dependency (amod, appos, or compound) for descriptive terms
                        if token.dep_ in ("amod", "appos", "compound"):
                            relationships.append((entity_text, ent.label_, "is", token.text))
                # capture verb-based relationships (e.g., actions like "conducted research")
                if token.pos_ == "VERB" and any(child.dep_ in ("dobj", "pobj") for child in token.children):
                    for child in token.children:
                        if child.dep_ in ("dobj", "pobj") and not any(e.start <= child.i <= e.end for e in doc.ents if e.text != entity_text):
                            relationships.append((entity_text, ent.label_, token.text, child.text))
    return relationships

def entities_to_json(entities, relationships):
    nodes = []
    edges = []

    # Create unique nodes
    node_labels = set()
    for entity, entity_type in entities:
        if entity.lower() not in node_labels:
            node_labels.add(entity.lower())
            nodes.append({"Label": entity.lower()})

    # Create edges
    for source, source_type, relation, target in relationships:
        edge = {
            "Label": relation.lower(),
            "Source": source.lower(),
            "Target": target.lower()
        }
        edges.append(edge)

    return {
        "Nodes": nodes,
        "Edges": edges
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="helix knowledge workflow")
    parser.add_argument("input", help="input file path", nargs=1)
    parser.add_argument("-t", "--type", help="input doc type (pdf, ...)", default="pdf")
    parser.add_argument("-c", "--chunking_method", help="chunking method (recursive, semantic", default="recursive")
    args = parser.parse_args()

    in_doc = args.input[0]
    doc_type = args.type
    chunking_method = args.chunking_method

    # testing (620 chars)
    #sample_text = """
    #    Marie Curie, born on 7 November 1867 in Warsaw, Poland, was a brilliant physicist and chemist whose curiosity and perseverance changed the course of science. From a young age, Marie displayed an insatiable hunger for knowledge. Despite the limitations placed on women in education at the time, she pursued her studies with determination, eventually moving to Paris to attend the Sorbonne. There, she immersed herself in physics and mathematics, often studying late into the night, sustained only by her passion and the occasional crust of bread.
    #    It was at the Sorbonne that she met Pierre Curie, a quiet but brilliant physicist with whom she would form both a romantic and scientific partnership. Their shared fascination with the invisible forces of nature—particularly magnetism and radioactivity—brought them together. They married in 1895 and began working side by side in a makeshift laboratory, often in difficult and even dangerous conditions. In 1903, their tireless efforts led to the discovery of two new radioactive elements, polonium and radium, earning them, along with Henri Becquerel, the Nobel Prize in Physics. It was the first Nobel ever awarded to a woman.
    #    Tragedy struck in 1906 when Pierre was killed in a street accident. Grief-stricken but resolute, Marie took over his teaching position, becoming the first female professor at the University of Paris. She continued their work on radioactivity, eventually isolating radium in its pure form. Her pioneering research earned her a second Nobel Prize in 1911—this time in Chemistry—making her the first person to win Nobel Prizes in two different scientific fields. Her legacy of scientific excellence would continue through her children and grandchildren, with the Curie family ultimately earning five Nobel Prizes.
    #    And then, there was Robin Williams. A century later, in a very different field, his contagious energy and quicksilver wit lit up the world in a way that echoes Marie Curie's radiance—figuratively speaking. Though their lives couldn’t have been more different, Williams once joked during a stand-up set that Marie Curie must have been "the original glow stick," unknowingly blending comedy with an obscure nod to science. It’s easy to imagine that, had their paths somehow crossed across time and space, Robin would have found a way to make Marie laugh, while she would have quietly corrected his terminology—before handing him a lead apron, just in case.
    #"""

    md_text = convert_to_markdown(in_doc, doc_type)
    chunked_text = chunker(md_text)

    for chunk in chunked_text:
        doc = nlp(chunk)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        relationships = gen_ne(doc)

        ne = entities_to_json(entities, relationships)
        ne = [json_to_helix(json.dumps(ne))]

        print(len(ne[0][0]), "entities:", ne[0][0])
        print(len(ne[0][1]), "relationships:", ne[0][1])
        insert_e_r(chunk, ne[0][0], ne[0][1])


"""
spaCy’s en_core_web_sm model recognizes these entity types:
PERSON: People, including fictional.
NORP: Nationalities, religious, or political groups.
FAC: Buildings, airports, highways, etc.
ORG: Companies, agencies, institutions.
GPE: Countries, cities, states.
LOC: Non-GPE locations, e.g., mountain ranges, bodies of water.
PRODUCT: Objects, vehicles, foods, etc. (not services).
EVENT: Named hurricanes, battles, wars, sports events.
WORK_OF_ART: Titles of books, songs, etc.
LAW: Named documents made into laws.
LANGUAGE: Any named language.
DATE: Absolute or relative dates or periods.
TIME: Times smaller than a day.
PERCENT: Percentage, including "%".
MONEY: Monetary values, including unit.
QUANTITY: Measurements, as of weight or distance.
ORDINAL: "first", "second", etc.
CARDINAL: Numerals that do not fall under another type.
"""

