import helix
from typing import List

class hnswinserttext(helix.Query):
    def __init__(self, text_in: str):
        super().__init__()
        self.text_in = text_in
    def query(self): return [{ "text_in": self.text_in }]
    def response(self, response): return response

class hnswinsert(helix.Query):
    def __init__(self, vector: List[float]):
        super().__init__()
        self.vector = vector
    def query(self): return [{ "vector": self.vector }]
    def response(self, response): return response

db = helix.Client(local=True)

res = db.query(hnswinserttext("hello world!"))
print(res)

res = db.query(hnswinsert([2, 2, 2, 4]))
print(res)

