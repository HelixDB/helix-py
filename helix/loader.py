from helix.types import DataType, HELIX
import os
from typing import Set, List
#import pyarrow.parquet as pq # TODO: custom write

class Loader:
    def __init__(self, data_path: str):
        self.data_path: str = data_path
        self.data_type: DataType = self._check_data_type(data_path)
        print(f"{HELIX}: using data_type: '{self.data_type}'")
        self.files: List[str] = None

    def _check_data_type(self, data_path: str) -> DataType:
        if not os.path.isdir(data_path):
            raise ValueError(f"'{data_path}' is not a valud directory")

        self.files = [f for f in os.listdir(data_path) if os.path.isfile(os.path.join(data_path, f))]

        if not self.files:
            raise ValueError(f"no files found in directory '{data_path}'")

        found_types: Set[DataType] = set()

        for filename in self.files:
            _, ext = os.path.splitext(filename)

            try:
                data_type = next(dt for dt in DataType if dt.value == ext.lower())
                found_types.add(data_type)
            except StopIteration:
                raise ValueError(f"unsupported file type '{ext}' in file '{filename}'")

        if len(found_types) > 1:
            type_list = [t.name for t in found_types]
            raise ValueError(
                f"Multiple different data types found in directory '{data_path}': {', '.join(type_list)}"
            )

        return found_types.pop()

    def _parquet(self, cols: List[str]=None):
        raise NotImplementedError("Parquet file reading not yet implemented")

    def _arrow(self):
        raise NotImplementedError("Arrow file reading not yet implemented")

    def _fvecs(self):
        raise NotImplementedError("FVECS file reading not yet implemented")

    def _csv(self):
        raise NotImplementedError("CSV file reading not yet implemented")

    def get_data(self, cols: List[str]):
        data_type_methods = {
            DataType.PARQUET: self._parquet,
            DataType.ARROW: self._arrow,
            DataType.FVECS: self._fvecs,
            DataType.CSV: self._csv
        }
        method = data_type_methods(self.data_type)

        if method is None:
            raise ValueError(f"No method Found for data type: {self.data_path}")

        return method(cols)