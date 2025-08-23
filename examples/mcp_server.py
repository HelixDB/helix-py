from helix.client import Client
from helix.mcp import MCPServer, ToolConfig
import asyncio

# Create a Helix client
helix_client = Client(local=True)

# Disable tools (eg. search_vector_text)
tool_config = ToolConfig(search_vector_text=False)

# Create an MCP server
mcp_server = MCPServer("helix-mcp", helix_client, tool_config=tool_config)

# Run the MCP server
# Defaults to streamable-http transport on localhost port 8000
# mcp_server.run()

# Run the MCP server in the background (non-blocking)
mcp_server.run_bg()

# Run the MCP server asynchronously
# async def main():
#     await mcp_server.run_async()

# asyncio.run(main())