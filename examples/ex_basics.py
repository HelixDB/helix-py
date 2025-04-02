import helix
from helix.client import hnswinsert

db = helix.Client()
#dbpedia_data = helix.Loader("data/dpedia-openai-1m/", cols=["openai"]) # https://huggingface.co/datasets/KShivendu/dbpedia-entities-openai-1M
#gist_base_data = helix.Loader("data/ann-gist1m/") # http://corpus-texmex.irisa.fr/
scp_embeddings = helix.Loader("data/mnist_csv/mnist.csv", cols=["embedding"])
db.query(hnswinsert(scp_embeddings.get_data()[0]))



#vecs = db.query(HNSWSearch(query_vec, 10))
#print(vecs)