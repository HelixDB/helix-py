from helix.loader import Loader
from helix.types import GHELIX, RHELIX
import socket
import json
import urllib.request
import urllib.error

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
        # TODO: somehow check if endpoint is valid (or just check when trying to send)

    def query(self):
        pass

# sample default
class hnswinsert(Query):
    def __init__(self, data_loader: Loader):
        super().__init__(__class__.__name__)
        self.data_loader: Loader = data_loader

    def query(self):
        data = self.data_loader.get_data()
        payload = data[0][0]
        return payload

# sample default
class hnswsearch(Query):
    def __init__(self, query, k: int=10):
        super().__init__(__class__.__name__)
        self.query = query

    def query(self):
        pass

class Client:
    def __init__(self, url: str="https://0.0.0.0", port: int=6969):
        self.h_server_url = url
        self.h_server_port = port
        try:
            hostname = url.replace("http://", "").replace("https://", "").split("/")[0]
            socket.create_connection((hostname, port), timeout=5)
            print(f"{GHELIX} Helix instance found at '{hostname}:{port}'")
        except socket.error:
            raise Exception(f"no helix server found at '{url}:{port}'")

    def _construct_full_url(self, endpoint: str) -> str:
        return f"{self.h_server_url}:{self.h_server_port}/{endpoint}"

    # (they all gonna be POSTS anyway)
    def query(self, query: Query) -> bool:
        data = json.dumps(query.query()).encode("utf-8")
        ep = self._construct_full_url(query.endpoint)
        print(f"{GHELIX} sending request to {ep}")
        try:
            req = urllib.request.Request(
                ep,
                data=data,
                headers={"Content-Type": "application/json"},
                method='POST',
            )

            with urllib.request.urlopen(req) as response:
                return response.getcode() == 200

        except (urllib.error.URLError, urllib.error.HTTPError) as e:
            print(f"Insertion failed: {e}")
            return False