from numpy import float64 as npfloat64
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
    # TODO: probably some custom for when we do custom chunking and such

NP_FVec = NDArray[npfloat64]
Payload = Dict[str, Any]
JSONType = Union[Dict[str, Any], List[Any], str, int, float, bool, None]

# TODO: custom exceptions/errors
