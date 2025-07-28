import os
from pathlib import Path
from typing import Dict, List

class Schema:
    nonnumeric_types = [
        "ID",
        "Date",
        "String",
        "Boolean"
    ]

    F_types = [32, 64]
    I_types = [8, 16, 32, 64]
    U_types = [8, 16, 32, 64, 128]

    schema_file = "schema.hx"

    def __init__(self, config_path:str="helixdb-cfg"):
        self.config_path = config_path

        self.nodes = {}
        self.edges = {}
        self.vectors = {}
        self.output = ""

        self.helix_dir = Path(os.path.dirname(os.path.curdir)).resolve()
        os.makedirs(os.path.join(self.helix_dir, self.config_path), exist_ok=True)

        if not Path(os.path.join(self.helix_dir, self.config_path, Schema.schema_file)).exists():
            self.schema_path = os.path.join(self.helix_dir, self.config_path, Schema.schema_file)
            open(self.schema_path, 'w').close()
            print("Schema file created")
        else:
            self.schema_path = os.path.join(self.helix_dir, self.config_path, Schema.schema_file)
            with open(self.schema_path, "r") as f:
                schema = f.read()
                schema = schema.split('\n\n')
                self._read_schema(schema)
                self._compile()
            print("Schema file loaded")

    def create_node(self, node_type:str, properties:Dict[str, str] = {}, index:List[str] = []):
        if not isinstance(node_type, str):
            raise TypeError(f"Node type must be a string, got {type(node_type).__name__}")
        if len(node_type) < 1:
            raise ValueError(f"Node type is empty")
        if not isinstance(properties, dict):
            raise TypeError(f"Properties must be a dictionary, got {type(properties).__name__}")

        self.nodes[node_type] = {"properties": properties, "index": index}

    def update_node(self, node_type:str, properties:Dict[str, str] = {}, index:List[str] = []):
        self.create_node(node_type, properties, index)

    def get_nodes(self):
        return self.nodes

    def get_node(self, node_type:str):
        return self.nodes.get(node_type)

    def delete_node(self, node_type:str):
        if node_type in self.nodes:
            del self.nodes[node_type]
        else:
            raise ValueError(f"Node type {node_type} does not exist")
    
    def delete_nodes(self, node_types:List[str]):
        for node_type in node_types:
            self.delete_node(node_type)

    def create_edge(self, edge_type:str, from_node:str, to_node:str, properties:Dict[str, str] = {}):
        if not isinstance(edge_type, str):
            raise TypeError(f"Edge type must be a string, got {type(edge_type).__name__}")
        if len(edge_type) < 1:
            raise ValueError(f"Edge type is empty")
        if not isinstance(from_node, str):
            raise TypeError(f"From node must be a string, got {type(from_node).__name__}")
        if len(from_node) < 1:
            raise ValueError(f"From node is empty")
        if not isinstance(to_node, str):
            raise TypeError(f"To node must be a string, got {type(to_node).__name__}")
        if len(to_node) < 1:
            raise ValueError(f"To node is empty")
        if not isinstance(properties, dict):
            raise TypeError(f"Properties must be a dictionary, got {type(properties).__name__}")

        self.edges[edge_type] = {"from": from_node, "to": to_node, "properties": properties}

    def update_edge(self, edge_type:str, from_node:str, to_node:str, properties:Dict[str, str] = {}):
        self.create_edge(edge_type, from_node, to_node, properties)

    def get_edges(self):
        return self.edges

    def get_edge(self, edge_type:str):
        return self.edges.get(edge_type)

    def delete_edge(self, edge_type:str):
        if edge_type in self.edges:
            del self.edges[edge_type]
        else:
            raise ValueError(f"Edge type {edge_type} does not exist")
    
    def delete_edges(self, edge_types:List[str]):
        for edge_type in edge_types:
            self.delete_edge(edge_type)

    def create_vector(self, vector_type:str, properties:Dict[str, str] = {}):
        if not isinstance(vector_type, str):
            raise ValueError("Vector type must be a string")
        if len(vector_type) < 1:
            raise ValueError("Vector type must be at least 1 character long")
        if not isinstance(properties, dict):
            raise ValueError("Properties must be a dictionary")

        self.vectors[vector_type] = {"properties": properties}

    def update_vector(self, vector_type:str, properties:Dict[str, str] = {}):
        self.create_vector(vector_type, properties)

    def get_vectors(self):
        return self.vectors

    def get_vector(self, vector_type:str):
        return self.vectors.get(vector_type)

    def delete_vector(self, vector_type:str):
        if vector_type in self.vectors:
            del self.vectors[vector_type]
        else:
            raise ValueError(f"Vector type {vector_type} does not exist")
    
    def delete_vectors(self, vector_types:List[str]):
        for vector_type in vector_types:
            self.delete_vector(vector_type)

    def clear(self):
        self.nodes = {}
        self.edges = {}
        self.vectors = {}
        self.output = ""

    def save(self) -> None:
        self._compile()
        with open(self.schema_path, "w") as f:
            f.write(self.output)

    def show_schema(self) -> str:
        self._compile()
        print(self.output)
        return self.output
    
    def _read_schema(self, schema:str):
        for element in schema:
            if len(element) < 1:
                continue
            element_type = element.split("::")[0]
            match element_type:
                case "N":
                    self._read_node(element)
                case "E":
                    self._read_edge(element)
                case "V":
                    self._read_vector(element)
                case _:
                    self._read_node(element)

    def _check_type(type: str):
        if type in Schema.nonnumeric_types:
            return True

        if type[0] == "[" and type[-1] == "]":
            return Schema._check_type(type[1:-1])
        
        if type[0] == "F":
            try:
                bits = int(type[1:])
            except ValueError:
                return False
            if bits in Schema.F_types:
                return True

        if type[0] == "I":
            try:
                bits = int(type[1:])
            except ValueError:
                return False
            if bits in Schema.I_types:
                return True

        if type[0] == "U":
            try:
                bits = int(type[1:])
            except ValueError:
                return False
            if bits in Schema.U_types:
                return True

        return False

    def _check_valid_property(key, value):
        if not isinstance(key, str):
            raise TypeError(f"Property key {key} must be a string, got {type(key).__name__}")
        if len(key) < 1:
            raise ValueError(f"Property key for {value} is empty")
        if not isinstance(value, str):
            raise TypeError(f"Property value for {key} must be a string, got {type(value).__name__}")
        if len(value) < 1:
            raise ValueError(f"Property value for {key} is empty")
        if not Schema._check_type(value):
            raise ValueError(f"Property {key}: {value} is not a valid type")

    def _read_node(self, node_str:str):
        node_str = node_str.replace("\n", "")
        node_type = node_str.split("::")[1].split("{")[0].strip()
        
        properties = {}
        index = []
        for item in node_str.split("{")[1].split("}")[0].strip(",").split(", "):
            item = item.replace(",", "").split(":")
            key = item[0].strip()
            value = item[1].strip()

            if key.startswith("INDEX"):
                new_key = key.replace("INDEX ", "").strip()
                index.append(new_key)
                properties[new_key] = value
            else:
                properties[key] = value
        
        self.create_node(node_type, properties, index)

    def _compile_node(self, node_type, properties):
        index = properties.get("index", [])
        properties = properties.get("properties", {})
        output = ""
        output += "N::" + node_type + " {\n"
        for key in index:
            Schema._check_valid_property(key, properties.get(key))
            output += "    INDEX " + key + ": " + properties.get(key) + ",\n"
        for key, value in properties.items():
            if key not in index:
                Schema._check_valid_property(key, value)
                output += "    " + key + ": " + value + ",\n"

        if len(properties) > 0:
            output = output[:-2] + "\n"
        output += "}\n\n"

        self.output += output

    def _read_edge(self, edge_str:str):
        edge_str = edge_str.replace("\n", "")
        edge_type = edge_str.split("::")[1].split("{")[0].strip()
        properties = {}
        edge_inside = ('{'.join(edge_str.split("{")[1:]).removesuffix("}")).strip(",").split(", ")
        from_node = edge_inside[0].split(":")[1].strip()
        to_node = edge_inside[1].split(":")[1].strip()
        prop_str = ','.join(edge_inside[2:]).replace("Properties: ", "").replace("{", "").replace("}", "")

        for item in prop_str.split(","):
            item = item.strip()
            if ':' not in item:
                continue
            key = item.split(":")[0].strip()
            value = item.split(":")[1].strip()
            properties[key] = value

        self.create_edge(edge_type, from_node, to_node, properties)

    def _compile_edge(self, edge_type, properties):
        from_node = properties.get("from")
        to_node = properties.get("to")
        properties = properties.get("properties", {})

        if from_node not in self.nodes and from_node not in self.vectors:
            raise ValueError(f"From node {from_node} does not exist")
        if to_node not in self.nodes and to_node not in self.vectors:
            raise ValueError(f"To node {to_node} does not exist")
        
        output = ""
        output += "E::" + edge_type + " {\n"
        output += "    From: " + from_node + ",\n"
        output += "    To: " + to_node + ",\n"
        output += "    Properties: {\n"
        for key, value in properties.items():
            Schema._check_valid_property(key, value)
            output += "        " + str(key) + ": " + str(value) + ",\n"
        if len(properties) > 0:
            output = output[:-2] + "\n"
        output += "    }\n"
        output += "}\n\n"

        self.output += output

    def _read_vector(self, vector_str:str):
        vector_str = vector_str.replace("\n", "")
        vector_type = vector_str.split("::")[1].split("{")[0].strip(",").strip()
        properties = {}
        for item in vector_str.split("{")[1].split("}")[0].split(", "):
            item = item.replace(",", "").split(":")
            properties[item[0].strip()] = item[1].strip()
        
        self.create_vector(vector_type, properties)

    def _compile_vector(self, vector_type:str, properties:Dict[str, str] = {}):
        properties = properties.get("properties", {})
        output = ""
        output += "V::" + vector_type + " {\n"
        for key, value in properties.items():
            Schema._check_valid_property(key, value)
            output += "    " + str(key) + ": " + str(value) + ",\n"
        if len(properties) > 0:
            output = output[:-2] + "\n"
        output += "}\n\n"
    
        self.output += output

    def _compile(self):
        self.output = ""
        for node_type, properties in self.nodes.items():
            self._compile_node(node_type, properties)
        for edge_type, properties in self.edges.items():
            self._compile_edge(edge_type, properties)
        for vector_type, properties in self.vectors.items():
            self._compile_vector(vector_type, properties)

    def __str__(self) -> str:
        self._compile()
        return self.output

    def __repr__(self) -> str:
        return self.__str__()
        