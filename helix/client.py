from helix.loader import Loader
from helix.types import GHELIX, RHELIX, Payload
import socket
import json
import urllib.request
import urllib.error
from typing import List, Optional, Any
from abc import ABC, abstractmethod
import numpy as np
from tqdm import tqdm
import sys

class Query(ABC):
    def __init__(self, endpoint: Optional[str]=None):
        self.endpoint = endpoint or self.__class__.__name__

    @abstractmethod
    def query(self) -> List[Payload]: pass

    @abstractmethod
    def response(self, response): pass

class hnswinsert(Query):
    def __init__(self, vector):
        super().__init__()
        self.vector = vector.tolist() if isinstance(vector, np.ndarray) else vector

    def query(self) -> List[Payload]:
        return [{ "vector": self.vector }]

    def response(self, response) -> Any:
        return response.get("res") # TODO: id of inserted vector

class hnswload(Query):
    def __init__(self, data_loader: Loader, batch_size: int=600):
        super().__init__()
        self.data_loader: Loader = data_loader
        self.batch_size = batch_size

    def query(self) -> List[Payload]:
        data = self.data_loader.get_data()

        payloads = []
        for i in range(0, len(data), self.batch_size):
            batch = data[i:i + self.batch_size]
            payload = { "vectors": [vector.tolist() for vector in batch] }
            payloads.append(payload)

        return payloads

    def response(self, response) -> Any:
        return response.get("res")

class hnswsearch(Query):
    def __init__(self, query_vector: List[float], k: int=5):
        super().__init__()
        self.query_vector = query_vector
        self.k = k

    def query(self) -> List[Payload]:
        return [{ "query": self.query_vector, "k": self.k }]

    def response(self, response) -> Any:
        try:
            vectors = response.get("res")
            return [(vector["id"], np.array(vector["data"], dtype=np.float64)) for vector in vectors]
        except json.JSONDecodeError:
            #print(f"{RHELIX} Failed to parse response as JSON", file=sys.stderr)
            return None

# mcp server queries
class init(Query):
    def __init__(self, addr: str, port: int):
        super().__init__(endpoint="mcp/" + self.__class__.__name__)
        self.connection_addr = addr
        self.connection_port = port
    def query(self) -> List[Payload]:
        return [{
            "connection_addr": self.connection_addr,
            "connection_port": self.connection_port,
        }]
    def response(self, response):
        return response # conn id

class call_tool(Query):
    def __init__(self, payload: dict):
        super().__init__(endpoint="mcp/" + self.__class__.__name__)
        self.connection_id = payload.get("connection_id")
        self.tool = payload.get("tool")
        self.args = payload.get("args")
    def query(self) -> List[Payload]:
        return [{
            "connection_id": self.connection_id,
            "tool": self.tool,
            "args": self.args,
        }]
    def response(self, response):
        return response

class next(Query):
    def __init__(self, conn_id: str):
        super().__init__(endpoint="mcp/" + self.__class__.__name__)
        self.connection_id = conn_id
    def query(self) -> List[Payload]:
        return [{"connection_id": self.connection_id}]
    def response(self, response):
        return response

# TODO: have the server spin-up automatically when running or
#   have it running already before starting script
#   maybe try a .init to start from python script
class Client:
    def __init__(self, local: bool, port: int=6969, api_endpoint: str=""):
        self.h_server_port = port
        self.h_server_api_endpoint = "" if local else api_endpoint
        self.h_server_url = "http://0.0.0.0" if local else ("https://api.helix-db.com/" + self.h_server_api_endpoint)
        try:
            hostname = self.h_server_url.replace("http://", "").replace("https://", "").split("/")[0]
            socket.create_connection((hostname, self.h_server_port), timeout=5)
            #print(f"{GHELIX} Helix instance found at '{self.h_server_url}:{self.h_server_port}'", file=sys.stderr)
        except socket.error:
            raise Exception(f"{RHELIX} No helix server found at '{self.h_server_url}:{self.h_server_port}'")

    def _construct_full_url(self, endpoint: str) -> str:
        return f"{self.h_server_url}:{self.h_server_port}/{endpoint}"

    def query(self, query: Query) -> List[Any]:
        query_data = query.query()
        ep = self._construct_full_url(query.endpoint)
        total = len(query_data) if hasattr(query_data, "__len__") else None
        responses = []

        for d in query_data:
        #for d in tqdm(query_data, total=total, desc=f"{GHELIX} Querying '{ep}'", file=sys.stderr):
            req_data = json.dumps(d).encode("utf-8")
            try:
                req = urllib.request.Request(
                    ep,
                    data=req_data,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )

                with urllib.request.urlopen(req) as response:
                    if response.getcode() == 200:
                        responses.append(query.response(json.loads(response.read().decode("utf-8"))))
            except (urllib.error.URLError, urllib.error.HTTPError) as e:
                #print(f"{RHELIX} Query failed: {e}", file=sys.stderr)
                responses.append(None)

        return responses
