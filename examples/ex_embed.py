import helix
from helix.client import hnswinsert

db = helix.Client()
# doesn't work because csv not working yet
anthropic_economic_index = helix.Loader("data/anthropic-economic-index/onet_task_statements.csv", cols=["Task"])
embedder = helix.EmbeddingModel()
embeddings = embedder.batch_embed(anthropic_economic_index)

for e in embeddings:
    db.query(hnswinsert(e))