import importlib
import os
from pathlib import Path

def load_tools_from_directory(mcp_instance, client, tools_dir="tools"):
    """Load all MCP tools from Python files in a directory"""
    tools_path = Path(tools_dir)
    if not tools_path.exists():
        return
    
    for py_file in tools_path.glob("*.py"):
        if py_file.name.startswith("__"):
            continue
            
        module_name = py_file.stem
        spec = importlib.util.spec_from_file_location(module_name, py_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Look for a register function
        if hasattr(module, 'register_tools'):
            module.register_tools(mcp_instance, client)