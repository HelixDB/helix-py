from helix.loader import Loader
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

    def query(self):
        pass

    def insert(self):
        pass

    def delete(self):
        pass

# sample default
class HNSWLoad(Query):
    def __init__(self, data_loader: Loader):
        super().__init__(__name__)
        self.data_loader: Loader = data_loader

    def insert(self):
        data = self.data_loader.get_data()
        print(data[0])

        payload = { "data": data }

        return payload

# sample default
class HNSWSearch(Query):
    def __init__(self, query, k: int=10):
        super().__init__(__name__)
        self.query = query

    def query(self):
        pass

class Client:
    def __init__(self, url: str="https://localhost", port: int=80):
        self.h_server_url = url
        self.h_server_port = port
        #try:
        #    hostname = url.replace("http://", "").replace("https://", "").split("/")[0]
        #    socket.create_connection((hostname, port), timeout=5)
        #except socket.error:
        #    raise Exception(f"helix server not available at '{url}:{port}'")

    def _construct_full_url(self, endpoint: str) -> str:
        return f"{self.h_server_url}/{endpoint}"

    def query(self, query: Query):
        pass

    def delete(self):
        pass

    def insert(self, query: Query) -> bool:
        # call query.insert() or query.query()
        data = json.dumps
        try:
            req = urllib.request.Request(
                self._construct_full_url(query.endpoint),
                data=data,
                headers={"Content-Type": "application/json"}
            )

            with urllib.request.urlopen(req) as response:
                return response.getcode() == 200

        except (urllib.error.URLError, urllib.error.HTTPError) as e:
            print(f"Insertion failed: {e}")
            return False