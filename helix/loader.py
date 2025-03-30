from helix.types import DataType, GHELIX, RHELIX
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
        print(f"{GHELIX} Using data_type: '{self.data_type}'")

    def _check_data_type(self, data_path: str) -> DataType:
        if not os.path.exists(data_path):
            raise ValueError(f"{RHELIX} '{data_path}' does not exist")

        if os.path.isfile(data_path):
            filename = os.path.basename(data_path)
            self.data_path = os.path.dirname(data_path)
            self.files = [filename]

            _, ext = os.path.splitext(filename)
            try:
                data_type = next(dt for dt in DataType if dt.value == ext.lower())
                return data_type
            except StopIteration:
                raise ValueError(f"{RHELIX} Unsupported file type '{ext}' in file '{filename}'")
        elif os.path.isdir(data_path):
            self.data_path = data_path
            self.files = [f for f in os.listdir(data_path) if os.path.isfile(os.path.join(data_path, f))]
            if not self.files:
                raise ValueError(f"{RHELIX} No files found in directory '{data_path}'")
        else:
            raise ValueError(f"{RHELIX} '{data_path}' is not a valid file or directory")


        found_types: Set[DataType] = set()
        for filename in self.files:
            _, ext = os.path.splitext(filename)
            try:
                data_type = next(dt for dt in DataType if dt.value == ext.lower())
                found_types.add(data_type)
            except StopIteration:
                raise ValueError(f"{RHELIX} Unsupported file type '{ext}' in file '{filename}'")

        if len(found_types) > 1:
            type_list = [t.name for t in found_types]
            raise ValueError(
                f"{RHELIX} Multiple different data types found in '{data_path}': {', '.join(type_list)}"
            )

        return found_types.pop()

    def _parquet(self) -> List[Tuple[Any, ...]]:
        parquet_files = [f for f in self.files if f.endswith(".parquet")]
        if not parquet_files:
            raise ValueError(f"{RHELIX} No Parquet files found in directory '{self.data_path}'")

        all_data = []
        # TODO: tqdm by data point not by file
        for filename in tqdm(parquet_files, desc=f"{GHELIX} Loading Parquet Files", unit="File"):
            file_path = os.path.join(self.data_path, filename)
            table = pq.read_table(file_path)
            cols_to_read = self.cols if self.cols else table.column_names
            for col in cols_to_read:
                if col not in table.column_names:
                    raise ValueError(f"{RHELIX} Column '{col}' not found in file '{filename}'")
            column_data = [table.column(col).to_pylist() for col in cols_to_read]
            file_data = list(zip(*column_data))
            all_data.extend(file_data)

        return all_data

    def _arrow(self):
        raise NotImplementedError("{RHELIX} Arrow file reading not yet implemented")

    def _fvecs(self):
        raise NotImplementedError("{RHELIX} FVECS file reading not yet implemented")

    def _csv(self):
        raise NotImplementedError("{RHELIX} CSV file reading not yet implemented")

    def get_data(self):
        data_type_methods = {
            DataType.PARQUET: self._parquet,
            DataType.ARROW: self._arrow,
            DataType.FVECS: self._fvecs,
            DataType.CSV: self._csv
        }

        method = data_type_methods[self.data_type]

        if method is None:
            raise ValueError(f"{RHELIX} No method Found for data type: {self.data_path}")

        return method()