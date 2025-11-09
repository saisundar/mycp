# Optional Tool Configuration

This document explains how the Multi-Tool MCP Server now supports optional tool configuration, allowing you to use only the tools you need without requiring configuration for all services.

## Overview

Previously, the MCP server required configuration for **all** tools (Notion, Todoist, and Obsidian) to start. If any tool was missing its configuration, the entire server would crash.

**Now**, each tool is **optional**. The server will start with whatever tools are properly configured and show helpful warnings for any missing configuration.

## How It Works

### Startup Behavior

When you start the server, it attempts to load each tool module:

```bash
$ python main.py

============================================================
Multi-Tool MCP Server - Starting up...
============================================================
⚠ Notion tools not registered: NOTION_TOKEN environment variable is not set. Get one from https://www.notion.so/my-integrations
⚠ Todoist tools not registered: TODOIST_TOKEN environment variable is not set. Get one from https://todoist.com/app/settings/integrations
✓ Obsidian tools: LOADED
============================================================
✓ Server ready with tools: Obsidian
============================================================
```

### Environment Variables

Set these environment variables to enable each tool:

#### Notion
```bash
export NOTION_TOKEN=your_notion_integration_token
export NOTION_DATABASE_ID=your_default_database_id  # Optional
```

#### Todoist
```bash
export TODOIST_TOKEN=your_todoist_api_token
```

#### Obsidian
```bash
export OBSIDIAN_VAULT_PATH=/path/to/your/obsidian/vault
export OBSIDIAN_TEMPLATES_PATH=templates/  # Optional
```

### Runtime Behavior

If you call a tool that isn't configured, you'll get a clear error message:

```python
# Calling Notion tool without NOTION_TOKEN set
result = create_database_page(title="My Page")
# Returns: {"success": False, "error": "NOTION_TOKEN environment variable is not set..."}
```

## Configuration Examples

### Using Only Obsidian

```bash
export OBSIDIAN_VAULT_PATH=/Users/username/Documents/Obsidian/Vault
python main.py
```

Result: Only Obsidian tools are available, Notion and Todoist show warnings.

### Using Notion and Todoist (No Obsidian)

```bash
export NOTION_TOKEN=secret_token_123
export TODOIST_TOKEN=secret_token_456
python main.py
```

Result: Notion and Todoist tools are available, Obsidian shows a warning.

### Using All Tools

```bash
export NOTION_TOKEN=secret_token_123
export TODOIST_TOKEN=secret_token_456
export OBSIDIAN_VAULT_PATH=/Users/username/Documents/Obsidian/Vault
python main.py
```

Result: All tools are loaded and available.

## Benefits

1. **Flexibility**: Use only the tools you need
2. **No Crashes**: Server starts even with missing configuration
3. **Clear Feedback**: Know exactly which tools are loaded and why others aren't
4. **Easy Debugging**: Clear error messages guide you to fix configuration issues
5. **Gradual Adoption**: Add tools one at a time as you need them

## Troubleshooting

### "No tools loaded" message

This means none of the tools were properly configured. Check:
- Environment variables are set correctly
- Paths exist (for Obsidian vault)
- API tokens are valid

### Tool shows "NOT LOADED" but env var is set

Check the specific error message:
- **Invalid token**: The API token may be incorrect or expired
- **Path doesn't exist**: For Obsidian, verify the vault path exists
- **Missing dependencies**: Ensure all packages are installed (`pip install -r requirements.txt`)

### Tool loaded but doesn't work

If a tool loads but fails when called, it may be due to:
- Invalid API credentials
- Network connectivity issues
- Incorrect resource IDs (database IDs, project IDs, etc.)

## Architecture

The implementation uses a `register_tools()` function in each tool module that:
1. Checks configuration at registration time
2. Returns `False` if configuration is missing/invalid
3. Registers tools with the main FastMCP server if configuration is valid
4. Shows helpful warnings for missing configuration

This approach keeps the single-process architecture while making each tool truly optional.