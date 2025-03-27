from helix.types import DataType, HELIX
import os
from typing import Set, List, Tuple, Any
import pyarrow.parquet as pq # TODO: custom write
from tqdm import tqdm # TODO: write custom

class Loader:
    def __init__(self, data_path: str, cols: List[str]=None):
        self.files: List[str] = None
        self.data_path: str = data_path
        self.data_type: DataType = self._check_data_type(data_path)
        self.cols: List[str] = cols
        print(f"{HELIX}: using data_type: '{self.data_type}'")

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

    def _parquet(self) -> List[Tuple[Any, ...]]:
        parquet_files = [f for f in self.files if f.endswith(".parquet")]

        parquet_files = parquet_files[:-8] # NOTE: remove after testing

        if not parquet_files:
            raise ValueError(f"No Parquet files found in directory '{self.data_path}'")

        all_data = []

        # TODO: tqdm by data point not by file
        for filename in tqdm(parquet_files, desc="Loading Parquet Files", unit="File"):
            file_path = os.path.join(self.data_path, filename)
            table = pq.read_table(file_path)
            cols_to_read = self.cols if self.cols else table.column_names

            for col in cols_to_read:
                if col not in table.column_names:
                    raise ValueError(f"Column '{col}' not found in file '{filename}'")

            column_data = [table.column(col).to_pylist() for col in cols_to_read]

            file_data = list(zip(*column_data))
            all_data.extend(file_data)

        return all_data

    def _arrow(self):
        raise NotImplementedError("Arrow file reading not yet implemented")

    def _fvecs(self):
        raise NotImplementedError("FVECS file reading not yet implemented")

    def _csv(self):
        raise NotImplementedError("CSV file reading not yet implemented")

    def get_data(self):
        data_type_methods = {
            DataType.PARQUET: self._parquet,
            DataType.ARROW: self._arrow,
            DataType.FVECS: self._fvecs,
            DataType.CSV: self._csv
        }

        method = data_type_methods[self.data_type]

        if method is None:
            raise ValueError(f"No method Found for data type: {self.data_path}")

        return method()