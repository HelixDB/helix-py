from typing import List
from helix.loader import Loader
import socket

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
    def __init__(self, data: Loader):
        super().__init__(__name__)
        self.data = data

    def insert(self):
        data = self.data.get_data()

class HNSWSearch(Query):
    def __init__(self, query, k: int=10):
        super().__init__(__name__)
        self.query = query

    def query(self):
        pass

class Client:
    def __init__(self, url: str="https://localhost", port: int=80):
        self.hrserver_url = url
        self.hrserver_port = port
        #try:
        #    hostname = url.replace("http://", "").replace("https://", "").split("/")[0]
        #    socket.create_connection((hostname, port), timeout=5)
        #except socket.error:
        #    raise Exception(f"helix server not available at '{url}:{port}'")

    def query(self, query: Query):
        # call query.insert() or query.query()
        # create a json to send to query.endpoint via hserver
        pass