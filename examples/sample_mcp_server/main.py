from mcp.server.fastmcp import FastMCP
import helix
from typing import Optional, Tuple, List

mcp = FastMCP("helix-mcp")
client = helix.Client(local=True, port=6969)

@mcp.tool()
def init(connection_addr: str, connection_port: int) -> str:
    response = client.query(helix.init(connection_addr, connection_port))
    return response[0]

@mcp.tool()
def next(connection_id: str) -> str:
    response = client.query(helix.next(connection_id))
    return response[0]

@mcp.tool()
def out_step(connection_id: str, edge_label: str, edge_type: str) -> str:
    tool = "out_step"
    args = {
        "edge_label": edge_label,
        "edge_type": edge_type,
    }

    payload = {
        "connection_id": connection_id,
        "tool": tool,
        "args": args,
    }
    response = client.query(helix.call_tool(payload))
    return response[0]

@mcp.tool()
def out_e_step(connection_id: str, edge_label: str) -> str:
    tool = "out_e_step"
    args = { "edge_label": edge_label }

    payload = {
        "connection_id": connection_id,
        "tool": tool,
        "args": args,
    }
    response = client.query(helix.call_tool(payload))
    return response[0]

@mcp.tool()
def in_step(connection_id: str, edge_label: str, edge_type: str) -> str:
    tool = "in_step"
    args = {
        "edge_label": edge_label,
        "edge_type": edge_type,
    }

    payload = {
        "connection_id": connection_id,
        "tool": tool,
        "args": args,
    }
    response = client.query(helix.call_tool(payload))
    return response[0]

@mcp.tool()
def in_e_step(connection_id: str, edge_label: str) -> str:
    tool = "in_e_step"
    args = { "edge_label": edge_label }

    payload = {
        "connection_id": connection_id,
        "tool": tool,
        "args": args,
    }
    response = client.query(helix.call_tool(payload))
    return response[0]

@mcp.tool()
def n_from_type(connection_id: str, node_type: str) -> str:
    tool = "n_from_type"
    args = { "node_type": node_type }

    payload = {
        "connection_id": connection_id,
        "tool": tool,
        "args": args,
    }
    response = client.query(helix.call_tool(payload))
    return response[0]

@mcp.tool()
def e_from_type(connection_id: str, edge_type: str) -> str:
    tool = "e_from_type"
    args = { "edge_type": edge_type }

    payload = {
        "connection_id": connection_id,
        "tool": tool,
        "args": args,
    }
    response = client.query(helix.call_tool(payload))
    return response[0]

@mcp.tool()
def filter_items(
    connection_id: str,
    properties: Optional[List[Tuple[str, str]]]=None,
    filter_traversals: Optional[List[dict]]=None
) -> str:
    tool = "filter_items"
    args = {}
    if properties: args["properties"] = properties
    if filter_traversals: args["filter_traversals"] = filter_traversals

    payload = {
        "connection_id": connection_id,
        "tool": tool,
        "args": args,
    }
    response = client.query(helix.call_tool(payload))
    return response[0]

