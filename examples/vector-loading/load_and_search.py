from helix import Client, Loader
from helix.client import hnswinsert, hnswsearch

db = Client(local=True)
data = Loader("../../data/dpedia-openai-1m/train-00000-of-00026-3c7b99d1c7eda36e.parquet", cols=["openai"]) # https://huggingface.co/datasets/KShivendu/dbpedia-entities-openai-1M
for d in data.get_data()[:20]:
    ids = db.query(hnswinsert(d))

my_query = data.get_data()[1000].tolist()

vecs = db.query(hnswsearch(my_query))
print("search response:")
[print(vec) for vec in vecs]

