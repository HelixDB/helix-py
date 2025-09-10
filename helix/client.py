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
from concurrent.futures import ThreadPoolExecutor

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

class Client:
    """
    A client for interacting with the Helix server.

    Args:
        local (bool): Whether to use the local Helix server or not.
        port (int, optional): The port to use for the Helix server. Defaults to 6969.
        api_endpoint (str, optional): The API endpoint to use for the Helix server.
        verbose (bool, optional): Whether to print verbose output or not. Defaults to True.
        max_workers (int, optional): The maximum number of workers to use for concurrent requests. Defaults to 1.
    """
    def __init__(
        self, 
        local: bool, 
        port: int=6969, 
        api_endpoint: str="", 
        api_key: str=None, 
        verbose: bool=True,
        max_workers: int=1,
    ):
        self.h_server_port = port
        self.h_server_api_endpoint = "" if local else api_endpoint
        self.h_server_url = "http://127.0.0.1" if local else self.h_server_api_endpoint
        self.verbose = verbose
        self.local = local
        self.api_key = api_key
        self.max_workers = max_workers

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
    def query(self, query, payload: Optional[Payload|List[Payload]]=[]) -> List[Any]:
        """
        This is a dispatcher method that handles different types of queries.
        For the standard query method, it takes a string and a payload.
        For the custom query method, it takes a Query object.
        """
        pass

    @query.register
    def _(self, query: str, payload: Optional[Payload|List[Payload]]=[]) -> List[Any]:
        """
        Query the helix server with a string and a payload.

        Args:
            query (str): The query string.
            payload (Payload|List[Payload]): The payload to send with the query. Defaults to empty list.

        Returns:
            List[Any]: The response from the helix server.
        """
        full_endpoint = self._construct_full_url(query)
        total = len(payload) if isinstance(payload, list) else 1
        if isinstance(payload, list) and self.max_workers > 1 and len(payload) > 1:
            return self._send_reqs_batched(payload, total, full_endpoint)
        else:
            payload = payload if isinstance(payload, list) else [payload]
            payload = [{}] if len(payload) == 0 else payload
            return self._send_reqs(payload, total, full_endpoint, verbose=self.verbose)

    @query.register
    def _(self, query: Query, payload=[]) -> List[Any]:
        """
        Query the helix server with a Query object.

        Args:
            query (Query): The Query object to send with the query.
            payload (Any): This is not used for Query objects.

        Returns:
            List[Any]: The response from the helix server.
        """
        query_data = query.query()
        full_endpoint = self._construct_full_url(query.endpoint)
        total = len(query_data) if hasattr(query_data, "__len__") else None

        if isinstance(query_data, list) and self.max_workers > 1 and len(query_data) > 1:
            return self._send_reqs_batched(query_data, total, full_endpoint, query)
        else:
            return self._send_reqs(query_data, total, full_endpoint, query, verbose=self.verbose)

    def _send_reqs(self, data, total, endpoint, query: Optional[Query]=None, verbose: bool=True):
        """
        Send requests to the helix server.

        Args:
            data (List[Any]): The data to send.
            total (int, optional): The total number of requests to send. Defaults to None.
            endpoint (str): The endpoint to send the requests to.
            query (Query, optional): The Query object to send with the requests. Defaults to None.
            verbose (bool, optional): Whether to print verbose output or not. Defaults to True.

        Returns:
            List[Any]: The response from the helix server.
        """
        responses = []
        for d in tqdm(data, total=total, desc=f"{GHELIX} Querying '{endpoint}'", file=sys.stderr, disable=not verbose):
            req_data = json.dumps(d).encode("utf-8")
            try:
                req = urllib.request.Request(
                    endpoint,
                    data=req_data,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )

                if not self.local and self.api_key is not None:
                    req.add_header("x-api-key", self.api_key)

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

    def _send_reqs_batched(self, data, total, endpoint, query: Optional[Query]=None):
        """
        Send requests to the helix server in batches.

        Args:
            data (List[Any]): The data to send.
            total (int, optional): The total number of requests to send. Defaults to None.
            endpoint (str): The endpoint to send the requests to.
            query (Query, optional): The Query object to send with the requests. Defaults to None.

        Returns:
            List[Any]: The response from the helix server.
        """
        with ThreadPoolExecutor(max_workers=min(self.max_workers, len(data))) as executor:
            futures = [executor.submit(self._send_reqs, [d], 1, endpoint, query, False) for d in data]

            responses = []
            for future in tqdm(futures, total=len(futures), desc=f"{GHELIX} Querying '{endpoint}'", file=sys.stderr, disable=not self.verbose):
                responses.extend(future.result())

            return responses