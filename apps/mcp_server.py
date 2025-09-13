# For claude-desktop add this to ~/Library/Application Support/Claude/claude_desktop_config.json
#   adjusting the directory to where this file is located
"""
{
  "mcpServers": {
    "helix-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/ln/dev/helix-py/apps/mcp_server",
        "run",
        "--python", "3.11",
        "--with", "helix-py",
        "mcp_server.py"
      ]
    }
  }
}
"""

from helix.client import Client
from helix.mcp import MCPServer
from helix.embedding import OpenAIEmbedder
from dotenv import load_dotenv
load_dotenv()

# Create a Helix client
client = Client(local=True, port=6969)

# Create an embedder (optional, needs API key)
embedder = OpenAIEmbedder()

# Create an MCP server
mcp_server = MCPServer("helix-mcp", client, embedder=embedder)

if __name__ == "__main__":
  # Run the MCP server on stdio transport
  mcp_server.run(transport="stdio")

  # Run the MCP server on localhost port 8000 with streamable-http transport
  # mcp_server.run(transport="streamable-http", host="127.0.0.1", port=8000)