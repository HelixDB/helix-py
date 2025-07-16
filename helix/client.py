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
from functools import singledispatchmethod
import sys

class Query(ABC):
    """
    A base class for all queries.
    """
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
            print(f"{RHELIX} Failed to parse response as JSON", file=sys.stderr)
            return None

# mcp server queries
class init(Query):
    def __init__(self):
        # TODO: do this better/more simple
        super().__init__(endpoint="mcp/" + self.__class__.__name__)

    def query(self) -> List[Payload]:
        return [{}]

    def response(self, response):
        return response.get("res") # conn id

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

class schema_resource(Query):
    def __init__(self, conn_id: str):
        super().__init__(endpoint="mcp/" + self.__class__.__name__)
        self.connection_id = conn_id

    def query(self) -> List[Payload]:
        return [{"connection_id": self.connection_id}]

    def response(self, response):
        return response

class Client:
    """
    A client for interacting with the Helix server.

    Args:
        local (bool): Whether to use the local Helix server or not.
        port (int, optional): The port to use for the Helix server. Defaults to 6969.
        api_endpoint (str, optional): The API endpoint to use for the Helix server.
        verbose (bool, optional): Whether to print verbose output or not. Defaults to True.
    """
    def __init__(self, local: bool, port: int=6969, api_endpoint: str="", verbose: bool=True):
        self.h_server_port = port
        self.h_server_api_endpoint = "" if local else api_endpoint
        self.h_server_url = "http://0.0.0.0" if local else self.h_server_api_endpoint
        self.verbose = verbose
        self.local = local

        if local:
            try:
                hostname = self.h_server_url.replace("http://", "").replace("https://", "").split("/")[0]
                socket.create_connection((hostname, self.h_server_port), timeout=5)
                print(f"{GHELIX} Helix instance found at '{self.h_server_url}:{self.h_server_port}'", file=sys.stderr)
            except socket.error:
                raise Exception(f"{RHELIX} No helix server found at '{self.h_server_url}:{self.h_server_port}'")

    def _construct_full_url(self, endpoint: str) -> str:
        if self.local:
            return f"{self.h_server_url}:{self.h_server_port}/{endpoint}"
        else:
            return f"{self.h_server_url}/{endpoint}"

    @singledispatchmethod
    def query(self, query, payload) -> List[Any]:
        """
        This is a dispatcher method that handles different types of queries.
        For the standard query method, it takes a string and a payload.
        For the custom query method, it takes a Query object.
        """
        pass

    @query.register
    def _(self, query: str, payload: Payload|List[Payload]) -> List[Any]:
        """
        Query the helix server with a string and a payload.

        Args:
            query (str): The query string.
            payload (Payload|List[Payload]): The payload to send with the query.

        Returns:
            List[Any]: The response from the helix server.
        """
        full_endpoint = self._construct_full_url(query)
        total = len(payload) if isinstance(payload, list) else 1
        payload = payload if isinstance(payload, list) else [payload]
        payload = [{}] if len(payload) == 0 else payload

        return self._send_reqs(payload, total, full_endpoint)

    @query.register
    def _(self, query: Query, payload=None) -> List[Any]:
        """
        Query the helix server with a Query object.

        Args:
            query (Query): The Query object to send with the query.
            payload (Any, optional): The payload to send with the query. Defaults to None.

        Returns:
            List[Any]: The response from the helix server.
        """
        query_data = query.query()
        full_endpoint = self._construct_full_url(query.endpoint)
        total = len(query_data) if hasattr(query_data, "__len__") else None

        return self._send_reqs(query_data, total, full_endpoint, query)

    def _send_reqs(self, data, total, endpoint, query: Optional[Query]=None):
        """
        Send requests to the helix server.

        Args:
            data (List[Any]): The data to send.
            total (int, optional): The total number of requests to send. Defaults to None.
            endpoint (str): The endpoint to send the requests to.
            query (Query, optional): The Query object to send with the requests. Defaults to None.

        Returns:
            List[Any]: The response from the helix server.
        """
        responses = []
        for d in tqdm(data, total=total, desc=f"{GHELIX} Querying '{endpoint}'", file=sys.stderr, disable=not self.verbose):
            req_data = json.dumps(d).encode("utf-8")
            try:
                req = urllib.request.Request(
                    endpoint,
                    data=req_data,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )

                with urllib.request.urlopen(req) as response:
                    if response.getcode() == 200:
                        if query is not None:
                            responses.append(query.response(json.loads(response.read().decode("utf-8"))))
                        else:
                            responses.append(json.loads(response.read().decode("utf-8")))
            except (urllib.error.URLError, urllib.error.HTTPError) as e:
                print(f"{RHELIX} Query failed: {e}", file=sys.stderr)
                responses.append(None)

        return responses

