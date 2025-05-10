# import helix-py library and default queries
from helix import Client, Query, Loader
from helix.client import hnswinsert, hnswload, hnswsearch
from typing import Tuple

# setup a connection to a helix-db instance running locally
db = Client(local=True)

# load your data from parquet, fvecs, or csv files
data_loader = Loader("data/dpedia-openai-1m/train-00000-of-00026.parquet", cols=["openai"])

# -- for vectors using built-in hnsw queries

# to build the hnsw index make a query to helix with the hnswload query passing in your data_loader
ret_ids = db.query(hnswload(data_loader))

# insert a single element into the hnsw index
my_vector = [0.535224, 0.93842, -1.48294]
ret_id = db.query(hnswinsert(my_vector))

# search the hnsw index
my_search_vector = [1.48294, 0.18392, -1.48294]
vecs = db.query(hnswsearch(my_search_vector))

# -- for custom queries

# define what your query should handle in both the sending an receiveing part
# the end point of your helix-db instance should then be '/addUser'
class addUser(Query):
    def __init__(self, user: Tuple[str, int]):
        super().__init__()
        self.user = user
    def query(self):
        return [{ "Name": self.user[0], "Age": self.user[1] }]
    def response(self, response):
        pass

# calling db.query(addUser(("John", 24))) will then call the query method
#   you defined and send the data, if you are search/getting some sort of data
#   the response method that you define will then also automatically be called
#   handling the receiving of data from your helix-db instance

# you basically define exactly how you want to handle the data you are sending
#   and receiving via your python script so that you don't have to constantly
#   format or unpack data throughout your program
