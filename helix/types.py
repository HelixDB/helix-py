import numpy as np
from numpy.typing import NDArray
from enum import Enum
from typing import Dict, Any, Union, List

GHELIX = "\033[32m[HELIX]\033[0m"
RHELIX = "\033[31m[HELIX]\033[0m"

class DataType(Enum):
    PARQUET = ".parquet"
    ARROW = ".arrow"
    FVECS = ".fvecs"
    CSV = ".csv"

FVec = NDArray[np.float64]
Payload = Dict[str, Any]
JSONType = Union[Dict[str, Any], List[Any], str, int, float, bool, None]

#class HVector:
#    def __init__(self, id: str, data: FVec):
#        self.id = id
#        self.data = data
#        self.length = data.size
#
#    def euc_distance(self, other: "HVector") -> float:
#        if self.length != other.length: raise ValueError("{RHELIX} Both vectors must have the same length!")
#        return np.linalg.norm(self.data - other.data)

# TODO: custom exceptions/errors