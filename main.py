# EXAMPLE

import helix
from helix.client import HNSWSearch, HNSWLoad

#db = helix.Client()
dpedia_data = helix.Loader("data/dpedia-openai-1m", cols=["openai"])
test = HNSWLoad(dpedia_data)
test.insert()

#db.insert(HNSWLoad(dpedia_data))
#vecs = db.query(HNSWSearch(query_vec, k=10))





#import huggingface
#model = huggingface.import('llama3.2:1b')
#rag = helix.Rag(model, db)
#while True: prompt()