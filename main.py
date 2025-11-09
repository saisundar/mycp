#!/usr/bin/env python3
"""
Main FastMCP server for multi-tool integration.
Optimized for FastMCP Cloud deployment.

Tools are registered automatically when modules are imported.
Each tool checks its own configuration and registers only if properly configured.
"""

from mcp.server.fastmcp import FastMCP

# Initialize the FastMCP server - this is the entry point for FastMCP Cloud
mcp = FastMCP("multi-tool-server")

# Import tool modules - they will register themselves if configured
try:
    from tools import notion_tools

    notion_tools.register_tools(mcp)
except Exception as e:
    print(f"⚠ Notion tools not loaded: {e}")

try:
    from tools import todoist_tools

    todoist_tools.register_tools(mcp)
except Exception as e:
    print(f"⚠ Todoist tools not loaded: {e}")

try:
    from tools import obsidian_tools

    obsidian_tools.register_tools(mcp)
except Exception as e:
    print(f"⚠ Obsidian tools not loaded: {e}")

# The mcp instance is automatically used by FastMCP Cloud
# No need to call mcp.run() - the platform handles server lifecycle
