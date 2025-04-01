import helix
from helix.client import hnswinsert
from helix.embedder import EmbeddingModel

db = helix.Client()
#dbpedia_data = helix.Loader("data/dpedia-openai-1m/", cols=["openai"]) # https://huggingface.co/datasets/KShivendu/dbpedia-entities-openai-1M
scp_embeddings = helix.Loader("data/scp-embeddings/", cols=["embeddings"]) # https://huggingface.co/datasets/hevia/scp-embeddings
#gist_base_data = helix.Loader("data/ann-gist1m/") # http://corpus-texmex.irisa.fr/
db.query(hnswinsert(scp_embeddings.get_data()[0][0]))



#vecs = db.query(HNSWSearch(query_vec, 10))
#print(vecs)