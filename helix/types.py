import numpy as np
from numpy.typing import NDArray
from enum import Enum

HELIX = "\033[32m[HELIX]\033[0m"

class DataType(Enum):
    PARQUET = ".parquet"
    ARROW = ".arrow"
    FVECS = ".fvecs"
    CSV = ".csv"

FVec = NDArray[np.float64]

class HVector:
    def __init__(self, id: str, data: FVec):
        self.id = id
        self.data = data
        self.length = data.size

    def euc_distance(self, other: "HVector") -> float:
        if self.length != other.length: raise ValueError("Both vectors must have the same length!")
        return np.linalg.norm(self.data - other.data)

# TODO: custom exceptions