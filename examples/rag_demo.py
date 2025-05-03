from helix.client import Query
from helix.types import Payload, RHELIX
from json import JSONDecodeError
from typing import List, Tuple

class ragloaddocs(Query):
    def __init__(self, docs: List[Tuple[str, List[List[float]]]]):
        super().__init__()
        self.docs = docs

    def query(self) -> List[Payload]: # TODO: batch send
        docs_payload = []
        for doc, vecs in self.docs:
            docs_payload.append({ "doc": doc, "vecs": vecs })

        return [{ "docs": docs_payload }]

    def response(self, response):
        return response.get("res")

class ragsearchdoc(Query):
    def __init__(self, query_vector: List[float]): # TODO: temp format for now
        super().__init__()
        self.query_vector = query_vector

    def query(self) -> List[Payload]:
        return [{ "query": self.query_vector }]

    def response(self, response): # TODO: proper response handle
        try:
            doc = response.get("doc_node", [])
            return doc
        except JSONDecodeError:
            print(f"{RHELIX} Failed to parse response as JSON")
            return None

if __name__ == "__main__":
    pass