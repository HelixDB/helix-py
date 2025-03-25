# TODO: be able to load parquet, arrow, csv, pdfs, markdown in that order

#from typing import List
from types import HVector

# any/all queries
class HelixLoader:
    def __init__(self, data_path: str):
        self.data_path = data_path

# hnsw index specific queries
class HNSWLoader(HelixLoader):
    def __init__(self, data_path: str):
        super().__init__(data_path)

# graph specific queries
class GraphLoader(HelixLoader):
    def __init__(self, data_path: str):
        super().__init__(data_path)