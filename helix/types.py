import numpy as np
from numpy.typing import NDArray

FloatVector = NDArray[np.float64]

class HVector:
    def __init__(self, id: str, data: FloatVector):
        self.id = id
        self.data = data
        self.length = data.size

    def euc_distance(self, other: "HVector") -> float:
        if self.length != other.length: raise ValueError("Both vectors must have the same length!")
        return np.linalg.norm(self.data - other.data)
