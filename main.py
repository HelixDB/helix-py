# EXAMPLE

import helix
from helix.client import hnswsearch, hnswinsert

db = helix.Client()
dpedia_data = helix.Loader("data/dpedia-openai-1m", cols=["openai"])
res = db.insert(hnswinsert(dpedia_data))
print(res)
#vecs = db.query(HNSWSearch(query_vec, k=10))
#print(vecs)





#import huggingface
#model = huggingface.import('llama3.2:1b')
#rag = helix.Rag(model, db)
#while True: prompt()