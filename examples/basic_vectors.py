import helix
from helix.client import hnswinsert, hnswload, hnswsearch

db = helix.Client(local=True)

#data = helix.Loader("data/dpedia-openai-1m/train-00000-of-00026-3c7b99d1c7eda36e.parquet", cols=["openai"]) # https://huggingface.co/datasets/KShivendu/dbpedia-entities-openai-1M
#data = helix.Loader("data/ann-gist1m/") # http://corpus-texmex.irisa.fr/
data = helix.Loader("data/mnist_csv/", cols=["embedding"])

#db.query(hnswinsert(data.get_data()[0]))
db.query(hnswload(data))

#my_query = data.get_data()[1000][0].tolist()
#print("query:", my_query[:1535])

#vecs = db.query(hnswsearch(my_query, k=10))
#print("search response:")
#[print(vec[:1535]) for vec in vecs]
