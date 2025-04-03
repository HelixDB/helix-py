import helix
from helix.client import hnswinsert

db = helix.Client()
dbpedia_data = helix.Loader("data/dpedia-openai-1m/", cols=["openai"]) # https://huggingface.co/datasets/KShivendu/dbpedia-entities-openai-1M
#gist_base_data = helix.Loader("data/ann-gist1m/") # http://corpus-texmex.irisa.fr/
db.query(hnswinsert(dbpedia_data.get_data()[0])[0])

#vecs = db.query(HNSWSearch(query_vec, 10))
#print(vecs)