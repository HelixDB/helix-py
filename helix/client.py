from helix.loader import Loader
from helix.types import GHELIX, RHELIX, Payload, JSONType
import socket
import json
import urllib.request
import urllib.error
import http.client
from typing import List, Optional, Any
from abc import ABC, abstractmethod
import numpy as np

"""
Basically have multiple different query types based on what the input data looks like,
so instead instead of setting up a bunch of different types of loader, you can just define
your Query or use pre setup ones and go from there

Parent class for all other Query type objects that will be passed to the Client

each query basically has an insert or query method attached to it which is called when
passed into Client.query(). that's then called. you write the query or insert methods yourself
"""

class Query(ABC):
    def __init__(self, endpoint: Optional[str]=None):
        self.endpoint = endpoint or self.__class__.__name__
        # TODO: somehow check if endpoint is valid (or just check when trying to send)

    @abstractmethod
    def query(self) -> List[Payload]: pass

    @abstractmethod
    def response(self, response: JSONType) -> Any: pass

# IDEA: get and set hnsw params with ep
# server should send an error if theres already data and your trying to set configs
# otherwise should just return the curr config params

class hnswinsert(Query):
    def __init__(self, vector: List[float]):
        super().__init__()
        self.vector = vector

    def query(self) -> List[Payload]:
        return [{ "vector": self.vector }]

    def response(self, response: JSONType): # TODO: helix return id of inserted vector
        return None

class hnswload(Query):
    def __init__(self, data_loader: Loader):
        super().__init__()
        self.data_loader: Loader = data_loader

    def query(self) -> List[Payload]:
        data = self.data_loader.get_data()[:10]
        payload = [{ "vector": vector[0][0] } for vector in data]
        return payload

    def response(self, response: JSONType): return None # TODO: helix return ids of inserted vectors

class hnswsearch(Query):
    def __init__(self, query: List[float], k: int=10):
        super().__init__()
        self.query = query
        self.k = k

    def query(self) -> List[Payload]:
        return [{ "query": self.query, "k": self.k}]

    def response(self, response: JSONType):
        try:
            vectors = response.get("vectors", [])
            return np.array(vectors, dtype=np.float64)
        except json.JSONDecodeError:
            print(f"{RHELIX} Failed to parse response as JSON")
            return None

class Client:
    def __init__(self, url: str="http://0.0.0.0", port: int=6969):
        self.h_server_url = url
        self.h_server_port = port
        try:
            hostname = url.replace("http://", "").replace("https://", "").split("/")[0]
            socket.create_connection((hostname, port), timeout=5)
            print(f"{GHELIX} Helix instance found at '{url}:{port}'")
        except socket.error:
            raise Exception(f"{RHELIX} No helix server found at '{url}:{port}'")

    def _construct_full_url(self, endpoint: str) -> str:
        return f"{self.h_server_url}:{self.h_server_port}/{endpoint}"

    def query(self, query: Query) -> Any:
        for d in query.query():
            req_data = json.dumps(d).encode("utf-8")
            ep = self._construct_full_url(query.endpoint)
            print(f"{GHELIX} Sending request to {ep}")
            try:
                req = urllib.request.Request(
                    ep,
                    data=req_data,
                    headers={"Content-Type": "application/json"},
                    method='POST',
                )

                with urllib.request.urlopen(req) as response:
                    if response.getcode() == 200:
                        return query.response(json.loads(response.read().decode("utf-8")))
            except (urllib.error.URLError, urllib.error.HTTPError) as e:
                print(f"{RHELIX} Query failed: {e}")
                return None