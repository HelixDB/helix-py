# env vars?
# debug output on specific env var like DEBUG=1

from helix.client import Client, Query, init, next, call_tool, schema_resource, hnswinsert, hnswsearch
from helix.types import Payload, EdgeType, Hnode, Hedge, Hvector, json_to_helix
from helix.loader import Loader
from helix.instance import Instance
from helix.providers import OllamaClient, OpenAIClient

__version__ = "0.2.20"

