from typing import Dict, Any, Optional, List, Tuple, Any
from enum import Enum
import json
import sys

GHELIX = "\033[32m[HELIX]\033[0m"
RHELIX = "\033[31m[HELIX]\033[0m"

class DataType(Enum):
    PARQUET = ".parquet"
    ARROW = ".arrow"
    FVECS = ".fvecs"
    CSV = ".csv"
    # TODO: MARKDOWN = ".md"

Payload = Dict[str, Any]

class EdgeType(Enum):
    Vec = 1
    Node = 2

class Hnode:
    def __init__(
            self,
            label: str,
            properties: Optional[List[Tuple[str,  Any]]]
    ):
        self.label = label
        self.properties = properties
        self.id: Optional[int] = None

    def __str__(self) -> str:
        return f"Hnode(label={self.label}, id={self.id}, properties={self.properties})"

    def __repr__(self) -> str:
        return self.__str__()

class Hedge:
    def __init__(
            self,
            label: str,
            properties: Optional[List[Tuple[str,  Any]]],
            from_node_label: str,
            to_node_label: str,
            edge_type: EdgeType
    ):
        self.label = label
        self.properties = properties
        self.id: Optional[int] = None
        self.from_node_label = from_node_label
        self.to_node_label = to_node_label
        self.edge_type = edge_type

    def __str__(self) -> str:
        return (f"Hedge(label={self.label}, from={self.from_node_label}, "
                f"to={self.to_node_label}, type={self.edge_type}, id={self.id}, "
                f"properties={self.properties})")

    def __repr__(self) -> str:
        return self.__str__()

class Hvector(Hnode):
    def __init__(
            self,
            label: str,
            vector: List[float],
            properties: Optional[List[Tuple[str,  Any]]]
    ):
        super().__init__(label, properties)
        self.vector = vector

    def __str__(self) -> str:
        return f"Hvector(label={self.label}, id={self.id}, vector={self.vector}, properties={self.properties})"

    def __repr__(self) -> str:
        return self.__str__()

# here label pertains to a property and not the actual helix label stored
#   in the db. checkout apps/kg.py as to how it's used. the actual helix
#   label is something like "Entity" or "Relationship" (not in properties)
def json_to_helix(json_string: str) -> tuple[List[Hnode], List[Hedge]]:
    try:
        json_data = json.loads(json_string)
    except json.JSONDecodeError as e:
        print(f"{RHELIX} json decoding failed: {e}", file=sys.stderr)
        return [], []

    nodes = []
    edges = []

    label_to_node = {}
    for node_data in json_data.get("Nodes", []):
        label = node_data.get("Label")
        if not label: continue

        node = Hnode(label=label, properties=None)
        nodes.append(node)
        label_to_node[label] = node

    for edge_data in json_data.get("Edges", []):
        label = edge_data.get("Label")
        source_label = edge_data.get("Source")
        target_label = edge_data.get("Target")

        if not source_label: continue

        from_node = label_to_node.get(source_label)
        to_node = label_to_node.get(target_label)

        if from_node is None or to_node is None: continue

        edge = Hedge(
            label=label,
            properties=None,
            from_node_label=from_node.label,
            to_node_label=to_node.label,
            edge_type=EdgeType.Node
        )
        edges.append(edge)

    return nodes, edges

