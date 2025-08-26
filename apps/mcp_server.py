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
        "/Users/ln/dev/helix-py/apps/mcp_server",
        "run",
        "mcp_server.py"
      ]
    }
  }
}
"""

from helix.client import Client
from helix.mcp import MCPServer

# Create a Helix client
client = Client(local=True, port=6969)

# Create an MCP server
mcp_server = MCPServer("helix-mcp", client)

if __name__ == "__main__":
  # Run the MCP server on localhost port 8000 with streamable-http transport
  mcp_server.run(transport="streamable-http", host="127.0.0.1", port=8000)