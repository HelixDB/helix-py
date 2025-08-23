from helix.client import Client
from helix.mcp import MCPServer, ToolConfig

# Create a Helix client
helix_client = Client(local=True)

# Disable tools (eg. search_vector_text)
tool_config = ToolConfig(search_vector_text=False)

# Create an MCP server
mcp_server = MCPServer("helix-mcp", helix_client, tool_config=tool_config)

# Run the MCP server
# Defaults to streamable-http transport on localhost port 8000
mcp_server.run()

# Run the MCP server asynchronously
# mcp_server.run_async()