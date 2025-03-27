from helix.types import DataType, HELIX
import os
from typing import Set, List
#import pyarrow.parquet as pq # TODO: custom write

class Loader:
    def __init__(self, data_path: str):
        self.data_path: str = data_path
        self.data_type: DataType = self._check_data_type(data_path)
        print(f"{HELIX}: using data_type: '{self.data_type}'")

    def _check_data_type(self, data_path: str) -> DataType:
        if not os.path.isdir(data_path):
            raise ValueError(f"'{data_path}' is not a valud directory")

        files = [f for f in os.listdir(data_path) if os.path.isfile(os.path.join(data_path, f))]

        if not files:
            raise ValueError(f"no files found in directory '{data_path}'")

        found_types: Set[DataType] = set()

        for filename in files:
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

    def _parquet(self):
        pass

    def _arrow(self):
        pass

    def _fvecs(self):
        pass

    def _csv(self):
        pass

    def get_data(self, cols: List[str]) -> List:
        pass