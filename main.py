#!/usr/bin/env python3
"""
Main FastMCP server that aggregates all tool integrations.
Each tool module is loaded conditionally - if configuration is missing,
the tool won't be available but the server will continue to run.
"""

import sys

from mcp.server.fastmcp import FastMCP

# Import tool modules (they may fail if not configured, but we'll handle that below)
notion_error = None
try:
    from tools import notion_tools
except Exception as e:
    notion_tools = None
    notion_error = str(e)

todoist_error = None
try:
    from tools import todoist_tools
except Exception as e:
    todoist_tools = None
    todoist_error = str(e)

obsidian_error = None
try:
    from tools import obsidian_tools
except Exception as e:
    obsidian_tools = None
    obsidian_error = str(e)

# Initialize the FastMCP server
mcp = FastMCP("multi-tool-server")

# Track which tools are successfully loaded
loaded_tools = []

print("=" * 60, file=sys.stderr)
print("Multi-Tool MCP Server - Starting up...", file=sys.stderr)
print("=" * 60, file=sys.stderr)

# Try to register each tool module
# Tools that aren't configured will show warnings but won't crash the server

# Register Notion tools
try:
    if notion_tools and notion_tools.register_tools(mcp):
        loaded_tools.append("Notion")
        print("✓ Notion tools: LOADED", file=sys.stderr)
    else:
        print(
            f"✗ Notion tools: NOT LOADED - {notion_error or 'Unknown error'}",
            file=sys.stderr,
        )
except Exception as e:
    print(f"✗ Notion tools: NOT LOADED - {e}", file=sys.stderr)

# Register Todoist tools
try:
    if todoist_tools and todoist_tools.register_tools(mcp):
        loaded_tools.append("Todoist")
        print("✓ Todoist tools: LOADED", file=sys.stderr)
    else:
        print(
            f"✗ Todoist tools: NOT LOADED - {todoist_error or 'Unknown error'}",
            file=sys.stderr,
        )
except Exception as e:
    print(f"✗ Todoist tools: NOT LOADED - {e}", file=sys.stderr)

# Register Obsidian tools
try:
    if obsidian_tools and obsidian_tools.register_tools(mcp):
        loaded_tools.append("Obsidian")
        print("✓ Obsidian tools: LOADED", file=sys.stderr)
    else:
        print(
            f"✗ Obsidian tools: NOT LOADED - {obsidian_error or 'Unknown error'}",
            file=sys.stderr,
        )
except Exception as e:
    print(f"✗ Obsidian tools: NOT LOADED - {e}", file=sys.stderr)

# Print summary
print("=" * 60, file=sys.stderr)
if loaded_tools:
    print(f"✓ Server ready with tools: {', '.join(loaded_tools)}", file=sys.stderr)
else:
    print(
        "⚠ Warning: No tools loaded. Set environment variables to enable tools.",
        file=sys.stderr,
    )
print("=" * 60, file=sys.stderr)

if __name__ == "__main__":
    mcp.run()
