import helix

class insert_doc(helix.Query):
    def __init__(self, text: str):
        super().__init__()
        self.text = text
    def query(self): return [{ "doc": self.text }]
    def response(self, response): return response

db = helix.Client(local=True)

res = db.query(insert_doc("hello world!"))
print(res)

