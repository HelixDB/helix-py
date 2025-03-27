# EXAMPLE

import helix
from helix.client import HNSWSearch, HNSWInsert

db = helix.Client()
dpedia_data = helix.Loader("data/dpedia-openai-1m")
db.query(HNSWInsert(dpedia_data))
#vecs = db.query(HNSWSearch(k=10))






#import huggingface
#model = huggingface.import('llama3.2:1b')
#rag = helix.Rag(model, db)
#while True: prompt()