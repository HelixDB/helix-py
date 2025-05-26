from helix import Client, Loader
from helix.client import hnswinsert, hnswload, hnswsearch

db = Client(local=True)

#data = helix.Loader("data/dpedia-openai-1m/train-00000-of-00026-3c7b99d1c7eda36e.parquet", cols=["openai"]) # https://huggingface.co/datasets/KShivendu/dbpedia-entities-openai-1M
#data = helix.Loader("data/ann-gist1m/") # http://corpus-texmex.irisa.fr/
data = Loader("data/mnist_csv/", cols=["embedding"])

ids = db.query(hnswload(data))
print(ids)

#my_query = data.get_data()[1000].tolist()
##print("query:", my_query)
#
#vecs = db.query(hnswsearch(my_query))
#print("search response:")
#[print(vec) for vec in vecs]
