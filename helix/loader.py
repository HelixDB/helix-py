from helix.types import DataType, GHELIX, RHELIX
import os
import csv
from typing import Set, List, Tuple, Any, Optional
import numpy as np
from tqdm import tqdm # TODO: write custom (utils.py maybe)
import pyarrow.parquet as pq # TODO: custom write

# TODO: split between floating point data and text data
#   - start simple with some file types being only floats
#   and some only text (plain .txt for now)
class Loader:
    def __init__(self, data_path: str, cols: Optional[List[str]]=None):
        self.data_path: str = data_path
        self.data_type: DataType = self._check_data_type(data_path)
        self.cols: Optional[List[str]] = cols
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

    # TODO: can do without pyarrow as well
    #from parquet import ParquetFile
    #pf = ParquetFile('example.parquet')
    #for row in pf.iter_row_group(): print(row)

    def _parquet(self) -> List[Any]:
        parquet_files = [f for f in self.files if f.endswith(".parquet")]
        if not parquet_files:
            raise ValueError(f"{RHELIX} No Parquet files found in directory '{self.data_path}'")

        all_data = []

        for filename in parquet_files:
            file_path = os.path.join(self.data_path, filename)
            table = pq.read_table(file_path)

            cols_to_read = self.cols if self.cols else table.column_names

            for col in cols_to_read:
                if col not in table.column_names:
                    raise ValueError(f"{RHELIX} Column '{col}' not found in file '{filename}'")

            with tqdm(total=table.num_rows, desc=f"{GHELIX} Loading {filename}", unit="vectors") as pbar:
                arrays = [table.column(col).to_numpy() for col in cols_to_read]
                num_rows = len(arrays[0])
                batch_size = 10_000

                for batch_start in range(0, num_rows, batch_size):
                    batch_end = min(batch_start + batch_size, num_rows)

                    if len(cols_to_read) == 1:
                        batch_array = arrays[0][batch_start:batch_end]
                        batch_tuples = [item for item in batch_array]
                    else:
                        batch_data = [arr[batch_start:batch_end] for arr in arrays]
                        batch_tuples = list(zip(*batch_data))

                    all_data.extend(batch_tuples)
                    pbar.update(batch_end - batch_start)

        return all_data

    def _fvecs(self) -> List[Tuple[Any, ...]]:
        fvecs_files = [f for f in self.files if f.endswith(".fvecs")]
        if not fvecs_files:
            raise ValueError(f"{RHELIX} No FVECS files found in directory '{self.data_path}'")

        all_data = []
        total_vectors = 0

        for filename in fvecs_files:
            file_path = os.path.join(self.data_path, filename)
            vectors = []

            with open(file_path, 'rb') as f:
                pbar = tqdm(desc=f"{GHELIX} Loading {filename}", unit="vectors")

                while True:
                    try:
                        # read vector dims (first 4 bytes as int32)
                        dim_bytes = f.read(4)
                        if not dim_bytes: # eof
                            break

                        dim = np.frombuffer(dim_bytes, dtype=np.int32)[0]

                        # read vector data (dim * 4 bytes as float32)
                        vector_bytes = f.read(dim * 4)
                        if len(vector_bytes) < dim * 4: # incomplete vec
                            print(f"{RHELIX} Warning: Incomplete vector found in '{filename}', skipping")
                            break

                        vector = np.frombuffer(vector_bytes)
                        vectors.append(vector)

                        pbar.update(1)
                        total_vectors += 1

                        if len(vectors) >= 10_000:
                            batch_data = self._format_vector_batch(vectors)
                            all_data.extend(batch_data)
                            vectors = []

                    except Exception as e:
                        print(f"{RHELIX} Error reading vector from '{filename}': {e}")
                        break

                pbar.close()

                # process any remaining vectors
                if vectors:
                    batch_data = self._format_vector_batch(vectors)
                    all_data.extend(batch_data)

        print(f"{GHELIX} Loaded {total_vectors} vectors from {len(fvecs_files)} files")

        if not all_data:
            print(f"{RHELIX} Warning: No vectors found in any FVECS files")

        return all_data

    def _format_vector_batch(self, vectors):
        if self.cols:
            if len(self.cols) == 1:
                return [v for v in vectors]
            else:
                return [v + tuple(None for _ in range(len(self.cols) - 1)) for v in vectors]
        else:
            return [v for v in vectors]

    def _csv(self) -> List[Tuple[Any, ...]]:
        # TODO: cols isn't checked right now, fully assuming a (label,embedding, ...., embedding end) structure in the csv
        # TODO: can use pyarrow to speed up
        csv_files = [f for f in self.files if f.endswith(".csv")]
        if not csv_files:
            raise ValueError(f"{RHELIX} No CSV files found in directory '{self.data_path}'")

        all_vectors = []
        total_rows = 0

        for filename in csv_files:
            file_path = os.path.join(self.data_path, filename)
            vectors = []

            with open(file_path, 'r', encoding='utf-8') as f:
                header = f.readline().strip()

                pbar = tqdm(desc=f"{GHELIX} Loading {filename}", unit="rows")

                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    first_comma = line.find(',')
                    if first_comma == -1:
                        continue

                    embedding_str = line[first_comma+1:]

                    try:
                        embedding_values = [float(val) for val in embedding_str.split(',') if val.strip()]
                        embedding = np.array(embedding_values, dtype=np.float32)

                        vectors.append(embedding)
                        pbar.update(1)
                        total_rows += 1
                    except Exception as e:
                        print(f"{RHELIX} Error parsing row: {e}")

                pbar.close()

            all_vectors.extend(vectors)
            print(f"{GHELIX} Loaded {len(vectors)} vectors from {filename}")

        print(f"{GHELIX} Loaded {total_rows} vectors from {len(csv_files)} CSV files")

        return all_vectors

    def _arrow(self):
        raise NotImplementedError("{RHELIX} Arrow file reading not yet implemented")

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