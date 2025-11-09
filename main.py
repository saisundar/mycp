#!/usr/bin/env python3
"""
Main FastMCP server that aggregates all tool integrations.
"""

from mcp.server.fastmcp import FastMCP

from tools import notion_tools, obsidian_tools, todoist_tools

# Initialize the FastMCP server
mcp = FastMCP("multi-tool-server")

# Register all tool modules
mcp.include_router(notion_tools.router)
mcp.include_router(todoist_tools.router)
mcp.include_router(obsidian_tools.router)

if __name__ == "__main__":
    mcp.run()
