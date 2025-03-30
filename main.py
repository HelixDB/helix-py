import helix
from helix.client import hnswinsert

db = helix.Client(port=6971)
dpedia_data = helix.Loader("data/dpedia-openai-1m/train-00000-of-00026-3c7b99d1c7eda36e.parquet", cols=["openai"])
db.query(hnswinsert(dpedia_data.get_data()[0][0]))

#vecs = db.query(HNSWSearch(query_vec, 10))
#print(vecs)





#import huggingface
#model = huggingface.import('llama3.2:1b')
#rag = helix.Rag(model, db)
#while True: prompt()