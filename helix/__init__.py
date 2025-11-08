from helix.client import Client, Query
from helix.types import Payload, EdgeType, Hnode, Hedge, Hvector, json_to_helix
from helix.schema import Schema
from helix.instance import Instance

# Optional extra features

try:  # requires helix-py[loader]
    from helix.loader import Loader
except ImportError:
    pass

try:  # requires helix-py[chunking]
    from helix.chunk import Chunk
except ImportError:
    pass

try:  # requires helix-py[mcp]
    from helix.mcp import MCPServer, ToolConfig
except ImportError:
    pass

__version__ = "0.2.30"

