# $ uv venv && source .venv/bin/activate
# $ uv add <all the packages in pyproject.toml or from errors you get>
# then for claude-desktop add this to ~/Library/Application Support/Claude/claude_desktop_config.json
#   adjusting paths of course
"""
{
  "mcpServers": {
    "helix-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/ln/dev/helix-py/examples/sample_mcp_server",
        "run",
        "mcp_server.py"
      ]
    }
  }
}
"""

from fastmcp import FastMCP
import helix
from typing import Optional, Tuple, List
import sys
import dotenv

dotenv.load_dotenv()

mcp = FastMCP("helix-mcp")
client = helix.Client(local=True, port=6969)

@mcp.tool()
def call_tool() -> str:

    response = client.query("call_tool", {})
    return response[0]

@mcp.resource("config://{connection_id}/schema")
def schema_resource(connection_id: str) -> str:
    return client.query(helix.schema_resource(connection_id))[0]

@mcp.tool()
def out_step(connection_id: str, edge_label: str, edge_type: str) -> str:
    tool = "out_step"
    args = {
        "edge_label": edge_label,
        "edge_type": edge_type,
    }

    payload = {
        "connection_id": connection_id,
        "data": args,
    }
    response = client.query(helix.call_tool(tool, payload))
    print(f"res {response}", file=sys.stderr)
    return response[0]

@mcp.tool()
def out_e_step(connection_id: str, edge_label: str) -> str:
    tool = "out_e_step"
    args = { "edge_label": edge_label }

    payload = {
        "connection_id": connection_id,
        "data": args,
    }
    response = client.query(helix.call_tool(tool, payload))
    print(f"res {response}", file=sys.stderr)
    return response[0]

if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8000)

