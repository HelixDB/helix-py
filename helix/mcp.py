from __future__ import annotations
import sys
import asyncio
import threading
import json
from fastmcp import FastMCP
from fastmcp.tools.tool import Tool
from helix.client import Client
from helix.types import GHELIX, RHELIX
from helix.embedding.embedder import Embedder
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from enum import Enum

# ======================
# General Tools
# ======================

class ConnectionId(BaseModel):
    connection_id: str = Field(..., description="The connection id")

class Range(BaseModel):
    start: int = Field(0, description="The start of the range")
    end: int = Field(-1, description="The end of the range (-1 to get all items)")

class CollectArgs(BaseModel):
    connection_id: str = Field(..., description="The connection id")
    range: Optional[Range] = Field(None, description="The range of items to collect")
    drop: Optional[bool] = Field(True, description="Whether to reset the connection after collection")

class NFromTypeArgs(BaseModel):
    connection_id: str = Field(..., description="The connection id")
    node_type: str = Field(..., description="The label/name of node to retrieve")

class EFromTypeArgs(BaseModel):
    connection_id: str = Field(..., description="The connection id")
    edge_type: str = Field(..., description="The label/name of edge to retrieve")

# ======================
# Traversal Tools
# ======================

class EdgeTypes(Enum):
    node = "node"
    vec = "vec"

class OutStepArgs(BaseModel):
    connection_id: str = Field(..., description="The connection id")
    edge_type: EdgeTypes = Field(..., description="The target entity type. Use 'node' when traversing to nodes and 'vec' when traversing to vectors.")
    edge_label: str = Field(..., description="The label/name of edge to traverse out")

class OutEStepArgs(BaseModel):
    connection_id: str = Field(..., description="The connection id")
    edge_label: str = Field(..., description="The label/name of edge to traverse out")

class InStepArgs(BaseModel):
    connection_id: str = Field(..., description="The connection id")
    edge_type: EdgeTypes = Field(..., description="The target entity type. Use 'node' when traversing to nodes and 'vec' when traversing to vectors.")
    edge_label: str = Field(..., description="The label/name of edge to traverse into")

class InEStepArgs(BaseModel):
    connection_id: str = Field(..., description="The connection id")
    edge_label: str = Field(..., description="The label/name of edge to traverse into")

# ======================
# Filter Tool
# ======================

class Operator(Enum):
    eq = "=="
    neq = "!="
    gt = ">"
    gte = ">="
    lt = "<"
    lte = "<="

class FilterValue(BaseModel):
    key: str = Field(..., description="The key of the property")
    operator: Operator = Field(..., description="The operator to use")
    value: int | float | str | List[int | float | str] = Field(..., description=(
        "The value to filter. "
        "List to value and value to list comparisons will use the OR operator for each element in the list. "
        "List to list comparisons will also use the OR operator for each element in each list."
    ))

class ToolName(Enum):
    out_step = "out_step"
    out_e_step = "out_e_step"
    in_step = "in_step"
    in_e_step = "in_e_step"

class ToolArgs(BaseModel):
    edge_label: str = Field(..., description="The label/name of edge to traverse based on the tool")
    edge_type: Optional[EdgeTypes] = Field(None, description="The target entity type (node or vec)")
    filter: Optional[Filter] = Field(None, description="The filter to apply to the filter traversal results")

class FilterTraversal(BaseModel):
    tool_name: ToolName = Field(..., description="The name of the tool to use to do the filter traversal")
    args: ToolArgs = Field(..., description="The arguments to pass to the tool")

class Filter(BaseModel):
    properties: Optional[List[List[FilterValue]]] = Field(
        [], 
        description=(
            "OR-of-ANDs filter for current traversal results. "
            "The outer list represents an OR between property filters, meaning at least one of the inner lists must be true. "
            "The inner list represents an AND group of property filters, meaning all filters in the inner list must be true."
        )
    )
    filter_traversals: Optional[List[FilterTraversal]] = Field([], description=(
        "Does traversals based on the tool to filter the current traversal results by future traversal results. "
        "Uses AND logic, all traversal filters must be true."
    ))

class FilterArgs(BaseModel):
    connection_id: str = Field(..., description="The connection id")
    filter: Filter = Field(..., description="The filter to apply to the traversal results")

# ======================
# Search Tools
# ======================

class SearchVArgs(BaseModel):
    connection_id: str = Field(..., description="The connection id")
    query: str = Field(..., description="The text query to search")
    k: int = Field(10, description="The number of results to return")
    min_score: Optional[float] = Field(None, description="The minimum score to filter by (0.0 to 1.0)")

class SearchVTextArgs(BaseModel):
    connection_id: str = Field(..., description="The connection id")
    query: str = Field(..., description="The text query to search")
    label: str = Field(..., description="The label/name of the vector to search")

class SearchKeywordArgs(BaseModel):
    connection_id: str = Field(..., description="The connection id")
    query: str = Field(..., description="The text query to search")
    label: str = Field(..., description="The label/name of the node to search")
    limit: int = Field(10, description="The limit of results to return")

# ======================
# Tool Configs
# ======================

class ToolConfig(BaseModel):
    """
    Enable/disable MCP tools. Defaults to enabled.
    """
    n_from_type: bool = Field(True, description="Enable n_from_type tool")
    e_from_type: bool = Field(True, description="Enable e_from_type tool")
    out_step: bool = Field(True, description="Enable out_step tool")
    out_e_step: bool = Field(True, description="Enable out_e_step tool")
    in_step: bool = Field(True, description="Enable in_step tool")
    in_e_step: bool = Field(True, description="Enable in_e_step tool")
    filter_items: bool = Field(True, description="Enable filter tool")
    search_vector: bool = Field(True, description="Enable search_v tool")
    search_vector_text: bool = Field(True, description="Enable search_v_text tool")
    search_keyword: bool = Field(True, description="Enable search_keyword tool")
    

class MCPServer:
    """
    MCP server for HelixDB MCP endpoints. Specialized for graph traversal and search.

    Args:
        name (str): The name of the MCP server.
        client (Client): The Helix client.
        mcp_args (Optional[Dict[str, Any]]): Extra arguments to pass to the MCP server.
        verbose (bool): Whether to print verbose output.
        tool_config (ToolConfig): Enable/disable MCP tools.
        embedder (Optional[Embedder]): The embedder to use for vector search.

    Note:
        If embedder is not provided, search_vector tool will be disabled.
        If embedder is provided, search_vector_text tool will be disabled.
    """
    def __init__(
        self,
        name: str,
        client: Client,
        mcp_args: Optional[Dict[str, Any]] = {},
        verbose: bool=True,
        tool_config: ToolConfig = ToolConfig(),
        embedder: Optional[Embedder] = None,
        embedder_args: Optional[Dict[str, Any]] = {},
    ):
        self.mcp = FastMCP(name, **mcp_args)
        self.client = client
        self.verbose = verbose
        self.tool_config = tool_config
        self.embedder = embedder
        self.embedder_args = embedder_args
        if embedder is None:
            self.tool_config.search_vector = False
            self.tool_config.search_vector_text = True
        else:
            self.tool_config.search_vector = True
            self.tool_config.search_vector_text = False
        self._register_tools()

    def add_tool(self, tool: Tool):
        """
        Add a tool to the MCP server.

        Args:
            tool (Tool): The MCP tool to add.
        """
        self.mcp.add_tool(tool)

    def _register_tools(self) -> None:
        @self.mcp.tool()
        def init() -> str:
            """
            Initialize the MCP traversal connection

            Returns:
                str (The connection id)
            """
            try:
                if self.verbose: print(f"{GHELIX} MCP init", file=sys.stderr)
                result = self.client.query('mcp/init', {})[0]
                return "MCP init failed" if result is None else result
            except Exception as e:
                raise Exception(f"{RHELIX} MCP init failed: {e}")

        @self.mcp.tool(name="next")
        def next_item(args: ConnectionId) -> Dict[str, Any]:
            """
            Get the next item in the traversal results

            Returns:
                Dict[str, Any] (The next item)
            """
            try:
                if self.verbose: print(f"{GHELIX} MCP next", file=sys.stderr)
                result = self.client.query('mcp/next', {'connection_id': args.connection_id})[0]
                return {} if result is None else result
            except Exception as e:
                raise Exception(f"{RHELIX} MCP next failed: {e}")

        @self.mcp.tool()
        def collect(args: CollectArgs) -> List[Dict[str, Any]]:
            """
            Collect all items in the traversal results

            Returns:
                List[Dict[str, Any]] (List of collected items)
            """
            try:
                if self.verbose: print(f"{GHELIX} MCP collect", file=sys.stderr)
                payload = {'connection_id': args.connection_id}
                if args.range is not None: payload['range'] = args.range.model_dump()
                if not args.drop: payload['drop'] = args.drop
                result = self.client.query('mcp/collect', payload)[0]
                if isinstance(result, dict):
                    result = [result]
                return [] if result is None else result
            except Exception as e:
                raise Exception(f"{RHELIX} MCP collect failed: {e}")

        @self.mcp.tool()
        def reset(args: ConnectionId) -> str:
            """
            Reset the MCP traversal connection

            Returns:
                str (The connection id)
            """
            try:
                if self.verbose: print(f"{GHELIX} MCP reset", file=sys.stderr)
                result = self.client.query('mcp/reset', {'connection_id': args.connection_id})[0]
                return "MCP reset failed" if result is None else result
            except Exception as e:
                raise Exception(f"{RHELIX} MCP reset failed: {e}")

        @self.mcp.tool()
        def schema_resource(connection_id: str) -> Dict[str, Any]:
            """
            Get the schema for the given connection id

            Returns:
                {
                    "schema": {
                        "nodes": List[Dict[str, Any]],
                        "vectors": List[Dict[str, Any]],
                        "edges": List[Dict[str, Any]]
                    },
                    "queries": List[Dict[str, Any]]
                }
            """
            try:
                if self.verbose: print(f"{GHELIX} MCP schema_resource", file=sys.stderr)
                result = self.client.query('mcp/schema_resource', {'connection_id': connection_id})[0]
                result = json.loads(result)
                return {} if result is None else result
            except Exception as e:
                raise Exception(f"{RHELIX} MCP schema_resource failed: {e}")

        @self.mcp.tool(enabled=self.tool_config.n_from_type)
        def n_from_type(args: NFromTypeArgs) -> Dict[str, Any]:
            """
            Retrieves all nodes of a given type

            Returns:
                Dict[str, Any] (The first node of the given type)
            """
            try:
                if self.verbose: print(f"{GHELIX} MCP n_from_type", file=sys.stderr)
                result = self.client.query('mcp/n_from_type', {'connection_id': args.connection_id, 'data': {'node_type': args.node_type}})[0]
                return {} if result is None else result
            except Exception as e:
                raise Exception(f"{RHELIX} MCP n_from_type failed: {e}")

        @self.mcp.tool(enabled=self.tool_config.e_from_type)
        def e_from_type(args: EFromTypeArgs) -> Dict[str, Any]:
            """
            Retrieves all edges of a given type

            Returns:
                Dict[str, Any] (The first edge of the given type)
            """
            try:
                if self.verbose: print(f"{GHELIX} MCP e_from_type", file=sys.stderr)
                result =  self.client.query('mcp/e_from_type', {'connection_id': args.connection_id, 'data': {'edge_type': args.edge_type}})[0]
                return {} if result is None else result
            except Exception as e:
                raise Exception(f"{RHELIX} MCP e_from_type failed: {e}")

        @self.mcp.tool(enabled=self.tool_config.out_step)
        def out_step(args: OutStepArgs) -> Dict[str, Any]:
            """
            Traverses out from current nodes or vectors in the traversal with the given edge label to nodes or vectors. 
            Assumes that the current state of the traversal is a collection of nodes or vectors that is the source of the given edge label.

            Returns:
                Dict[str, Any] (The first node of the traversal result)
            """
            try:
                if self.verbose: print(f"{GHELIX} MCP out_step", file=sys.stderr)
                result = self.client.query('mcp/out_step', {'connection_id': args.connection_id, 'data': {'edge_label': args.edge_label, 'edge_type': args.edge_type.value}})[0]
                return {} if result is None else result
            except Exception as e:
                raise Exception(f"{RHELIX} MCP out_step failed: {e}")

        @self.mcp.tool(enabled=self.tool_config.out_e_step)
        def out_e_step(args: OutEStepArgs) -> Dict[str, Any]:
            """
            Traverses out from current nodes or vectors in the traversal to their edges with the given edge label. 
            Assumes that the current state of the traversal is a collection of nodes or vectors that is the source of the given edge label.

            Returns:
                Dict[str, Any] (The first edge of the traversal result)
            """
            try:
                if self.verbose: print(f"{GHELIX} MCP out_e_step", file=sys.stderr)
                result = self.client.query('mcp/out_e_step', {'connection_id': args.connection_id, 'data': {'edge_label': args.edge_label}})[0]
                return {} if result is None else result
            except Exception as e:
                raise Exception(f"{RHELIX} MCP out_e_step failed: {e}")

        @self.mcp.tool(enabled=self.tool_config.in_step)
        def in_step(args: InStepArgs) -> Dict[str, Any]:
            """
            Traverses in from current nodes or vectors in the traversal with the given edge label to nodes or vectors. 
            Assumes that the current state of the traversal is a collection of nodes or vectors that is the target of the given edge label.

            Returns:
                Dict[str, Any] (The first node of the traversal result)
            """
            try:
                if self.verbose: print(f"{GHELIX} MCP in_step", file=sys.stderr)
                result = self.client.query('mcp/in_step', {'connection_id': args.connection_id, 'data': {'edge_label': args.edge_label, 'edge_type': args.edge_type.value}})[0]
                return {} if result is None else result
            except Exception as e:
                raise Exception(f"{RHELIX} MCP in_step failed: {e}")

        @self.mcp.tool(enabled=self.tool_config.in_e_step)
        def in_e_step(args: InEStepArgs) -> Dict[str, Any]:
            """
            Traverses in from current nodes or vectors in the traversal to their edges with the given edge label. 
            Assumes that the current state of the traversal is a collection of nodes or vectors that is the target of the given edge label.

            Returns:
                Dict[str, Any] (The first edge of the traversal result)
            """
            try:
                if self.verbose: print(f"{GHELIX} MCP in_e_step", file=sys.stderr)
                result = self.client.query('mcp/in_e_step', {'connection_id': args.connection_id, 'data': {'edge_label': args.edge_label}})[0]
                return {} if result is None else result
            except Exception as e:
                raise Exception(f"{RHELIX} MCP in_e_step failed: {e}")

        @self.mcp.tool(enabled=self.tool_config.filter_items)
        def filter_items(args: FilterArgs) -> Dict[str, Any]:
            """
            Filters the current state of the traversal based on the given filter.

            Returns:
                Dict[str, Any] (The first item of the traversal result)
            """
            def _unwrap_filters(filters: Filter) -> Dict[str, Any]:
                properties = []
                for and_group in filters.properties:
                    and_filters = []
                    for and_filter in and_group:
                        and_filters.append({
                            "key": and_filter.key,
                            "operator": and_filter.operator.value,
                            "value": and_filter.value,
                        })
                    properties.append(and_filters)

                filter_traversals = []
                for filter_traversal in filters.filter_traversals:
                    tool_name = filter_traversal.tool_name.value
                    args = {"edge_label": filter_traversal.args.edge_label}
                    if filter_traversal.args.edge_type is not None:
                        args["edge_type"] = filter_traversal.args.edge_type.value
                    if filter_traversal.args.filter is not None:
                        args["filter"] = _unwrap_filters(filter_traversal.args.filter)
                    filter_traversals.append({"tool_name": tool_name, "args": args})

                return {
                    "properties": properties,
                    "filter_traversals": filter_traversals,
                }

            try:
                if self.verbose: print(f"{GHELIX} MCP filter", file=sys.stderr)
                filters = _unwrap_filters(args.filter)
                payload = {'connection_id': args.connection_id, 'data': {'filter': filters}}
                result = self.client.query('mcp/filter_items', payload)[0]
                return {} if result is None else result
            except Exception as e:
                raise Exception(f"{RHELIX} MCP filter failed: {e}")

        @self.mcp.tool(enabled=self.tool_config.search_vector)
        def search_vector(args: SearchVArgs) -> List[Dict[str, Any]]:
            """
            Similairity searches the vectors in the traversal based on the given vector. Assumes that the current state of the traversal is a collection of vectors.

            Returns:
                List[Dict[str, Any]] (The first k vectors of the traversal result ordered by descending similarity)
            """
            try:
                if self.verbose: print(f"{GHELIX} MCP search_vector", file=sys.stderr)
                vector = self.embedder.embed(args.query, **self.embedder_args)
                result = self.client.query('mcp/search_vector', {'connection_id': args.connection_id, 'data': {'vector': vector, 'k': args.k, 'min_score': args.min_score}})[0]
                if isinstance(result, dict):
                    result = [result]
                return [] if result is None else result
            except Exception as e:
                raise Exception(f"{RHELIX} MCP search_vector failed: {e}")

        @self.mcp.tool(enabled=self.tool_config.search_vector_text)
        def search_vector_text(args: SearchVTextArgs) -> List[Dict[str, Any]]:
            """
            Similairity searches the vectors in the traversal based on the given text query.

            Returns:
                List[Dict[str, Any]] (The first 5 vectors of the traversal result ordered by descending similarity)
            """
            try:
                if self.verbose: print(f"{GHELIX} MCP search_vector_text", file=sys.stderr)
                result = self.client.query('mcp/search_vector_text', {'connection_id': args.connection_id, 'data': {'query': args.query, 'label': args.label}})[0]
                return [] if result is None else result
            except Exception as e:
                raise Exception(f"{RHELIX} MCP search_vector_text failed: {e}")

        @self.mcp.tool(enabled=self.tool_config.search_keyword)
        def search_keyword(args: SearchKeywordArgs) -> List[Dict[str, Any]]:
            """
            BM25 searches the nodes in the traversal based on the given keyword query and the node label.

            Returns:
                List[Dict[str, Any]] (The first k nodes of the traversal result ordered by descending similarity where k is the limit)
            """
            try:
                if self.verbose: print(f"{GHELIX} MCP search_keyword", file=sys.stderr)
                result = self.client.query('mcp/search_keyword', {'connection_id': args.connection_id, 'data': {'query': args.query, 'label': args.label, 'limit': args.limit}})[0]
                if isinstance(result, dict):
                    return [result]
                return [] if result is None else result
            except Exception as e:
                raise Exception(f"{RHELIX} MCP search_keyword failed: {e}")

    def run(
        self,
        transport: str="streamable-http",
        host: str="127.0.0.1",
        port: int=8000,
        **run_args,
    ):
        """
        Run the MCP server.

        Args:
            transport (str, optional): The transport to use. Defaults to "streamable-http".
            host (str, optional): The host to use. Defaults to "127.0.0.1".
            port (int, optional): The port to use. Defaults to 8000.
            **run_args: Additional arguments to pass to the run method.
        """
        if transport == "stdio":
            self.mcp.run(transport="stdio")
        self.mcp.run(transport=transport, host=host, port=port, **run_args)

    async def run_async(
        self,
        transport: str="streamable-http",
        host: str="127.0.0.1",
        port: int=8000,
        **run_args,
    ):
        """
        Run the MCP server asynchronously.

        Args:
            transport (str, optional): The transport to use. Defaults to "streamable-http".
            host (str, optional): The host to use. Defaults to "127.0.0.1".
            port (int, optional): The port to use. Defaults to 8000.
            **run_args: Additional arguments to pass to the run method.
        """
        if transport == "stdio":
            self.mcp.run(transport="stdio")
        await self.mcp.run_async(transport=transport, host=host, port=port, **run_args)

    def run_bg(
        self,
        transport: str="streamable-http",
        host: str="127.0.0.1",
        port: int=8000,
        **run_args,
    ) -> threading.Thread:
        """
        Start the MCP server in a non-blocking background thread.

        Returns:
            threading.Thread: The daemon thread running the server.
        """
        def _runner():
            if transport == "stdio":
                self.mcp.run(transport="stdio")
            asyncio.run(self.mcp.run_async(transport=transport, host=host, port=port, **run_args))

        t = threading.Thread(target=_runner, daemon=True)
        t.start()
        return t