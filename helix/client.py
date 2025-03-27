from typing import List

class Client:
    def __init__(self, hserver: str="https://localhost:6969"):
        self.hserver = hserver
        # send a lil ping to make sure alive, if not raise Error

    def query(self, query: "Query"):
        pass

class Query:
    """
    Basically have multiple different query types based on what the input data looks like,
    so instead instead of setting up a bunch of different types of loader, you can just define
    your Query or use pre setup ones and go from there

    Parent class for all other Query type objects that will be passed to the Client

    each query basically has an insert or query method attached to it which is called when
    passed into Client.query(). that's then called. you write the query or insert methods yourself
    """
    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def query(self):
        pass

    def insert(self):
        pass

class HNSWInsert(Query):
    def __init__(self, data):
        super().__init__(__name__)

    def insert():
        pass

class HNSWSearch(Query):
    def __init__(self, query, k: int=10):
        super().__init__(__name__)
        self.query = query

    def query(self):
        pass