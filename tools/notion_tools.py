"""
Notion MCP Tools - CRUD operations for Notion workspaces
Optimized for FastMCP Cloud deployment with completely lazy loading
"""

import json
import sys
import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from notion_client import Client

# Lazy loading state - don't load anything at import time
_notion_token = None
_notion_client = None
_env_loaded = False
_DEFAULT_DATABASE_ID = None


def _load_env():
    """Load environment variables on first access."""
    global _notion_token, _DEFAULT_DATABASE_ID, _env_loaded
    if not _env_loaded:
        load_dotenv()
        _notion_token = os.getenv("NOTION_TOKEN")
        _DEFAULT_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
        _env_loaded = True


def _get_notion_client() -> Client:
    """
    Get or create Notion client lazily.
    Only initializes when first tool is called.
    """
    global _notion_client
    if _notion_client is None:
        _load_env()
        if not _notion_token:
            raise ValueError(
                "NOTION_TOKEN environment variable is not set. Get one from https://www.notion.so/my-integrations"
            )
        _notion_client = Client(auth=_notion_token)
    return _notion_client


def _check_config() -> tuple[bool, str]:
    """
    Check if Notion is properly configured and return status + message.
    This now also verifies the client can be initialized.
    """
    _load_env()

    if not _notion_token:
        return (
            False,
            "NOTION_TOKEN environment variable is not set. Get one from https://www.notion.so/my-integrations",
        )

    # Try to get client to verify it's valid
    try:
        _get_notion_client()
    except Exception as e:
        return False, f"Failed to initialize Notion client: {e}"

    return True, ""


def create_database_page(
    title: str,
    database_id: Optional[str] = None,
    properties: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create a new page in a Notion database.
    """
    # Check configuration at runtime
    is_configured, error_msg = _check_config()
    if not is_configured:
        return {"success": False, "error": error_msg}

    db_id = database_id or _DEFAULT_DATABASE_ID
    if not db_id:
        return {
            "success": False,
            "error": "No database_id provided and NOTION_DATABASE_ID environment variable is not set",
        }

    # Get client lazily
    notion = _get_notion_client()

    # Prepare the page properties
    page_properties = {"title": {"title": [{"text": {"content": title}}]}}

    # Add additional properties if provided
    if properties:
        if isinstance(properties, str):
            try:
                properties = json.loads(properties)
            except json.JSONDecodeError:
                return {
                    "success": False,
                    "error": "Properties must be valid JSON string or a dictionary",
                }

        page_properties.update(properties)

    try:
        response = notion.pages.create(
            parent={"database_id": db_id}, properties=page_properties
        )
        return {
            "success": True,
            "page_id": response["id"],
            "url": response["url"],
            "created_time": response["created_time"],
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_database(
    database_id: Optional[str] = None,
    filter_json: Optional[str] = None,
    sorts: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Query a Notion database and return pages.
    """
    is_configured, error_msg = _check_config()
    if not is_configured:
        return {"success": False, "error": error_msg}

    db_id = database_id or _DEFAULT_DATABASE_ID
    if not db_id:
        return {
            "success": False,
            "error": "No database_id provided and NOTION_DATABASE_ID environment variable is not set",
        }

    # Get client lazily
    notion = _get_notion_client()

    query_params = {}

    if filter_json:
        try:
            query_params["filter"] = json.loads(filter_json)
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "filter_json must be a valid JSON string",
            }

    if sorts:
        query_params["sorts"] = sorts

    try:
        response = notion.databases.query(database_id=db_id, **query_params)

        pages = []
        for page in response["results"]:
            pages.append(
                {
                    "id": page["id"],
                    "url": page["url"],
                    "created_time": page["created_time"],
                    "properties": page.get("properties", {}),
                }
            )

        return {
            "success": True,
            "pages": pages,
            "has_more": response.get("has_more", False),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_page(page_id: str) -> Dict[str, Any]:
    """
    Get a Notion page by ID and its content.
    """
    is_configured, error_msg = _check_config()
    if not is_configured:
        return {"success": False, "error": error_msg}

    # Get client lazily
    notion = _get_notion_client()

    # Extract page ID from URL if needed
    if "notion.so" in page_id:
        page_id = page_id.split("/")[-1].split("?")[0]

    try:
        # Get page metadata
        page = notion.pages.retrieve(page_id=page_id)

        # Get page content (blocks)
        blocks = notion.blocks.children.list(block_id=page_id)

        return {
            "success": True,
            "page": {
                "id": page["id"],
                "url": page["url"],
                "created_time": page["created_time"],
                "last_edited_time": page["last_edited_time"],
                "properties": page.get("properties", {}),
                "content_blocks": blocks.get("results", []),
            },
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def update_page(page_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update properties of a Notion page.
    """
    is_configured, error_msg = _check_config()
    if not is_configured:
        return {"success": False, "error": error_msg}

    # Get client lazily
    notion = _get_notion_client()

    # Extract page ID from URL if needed
    if "notion.so" in page_id:
        page_id = page_id.split("/")[-1].split("?")[0]

    # Parse properties if they're a JSON string
    if isinstance(properties, str):
        try:
            properties = json.loads(properties)
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Properties must be valid JSON string or a dictionary",
            }

    try:
        response = notion.pages.update(page_id=page_id, properties=properties)

        return {
            "success": True,
            "page_id": response["id"],
            "url": response["url"],
            "last_edited_time": response["last_edited_time"],
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_page(
    title: str, parent_page_id: Optional[str] = None, content: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a standalone Notion page (not in a database).
    """
    is_configured, error_msg = _check_config()
    if not is_configured:
        return {"success": False, "error": error_msg}

    # Get client lazily
    notion = _get_notion_client()

    # Prepare the page
    page_data = {"properties": {"title": {"title": [{"text": {"content": title}}]}}}

    # Set parent (either page or workspace root)
    if parent_page_id:
        if "notion.so" in parent_page_id:
            parent_page_id = parent_page_id.split("/")[-1].split("?")[0]
        page_data["parent"] = {"page_id": parent_page_id}
    else:
        page_data["parent"] = {"type": "workspace", "workspace": True}

    # Add content if provided
    if content:
        page_data["children"] = [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": content}}]
                },
            }
        ]

    try:
        response = notion.pages.create(**page_data)

        return {
            "success": True,
            "page_id": response["id"],
            "url": response["url"],
            "created_time": response["created_time"],
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def archive_page(page_id: str) -> Dict[str, Any]:
    """
    Archive (delete) a Notion page.
    """
    is_configured, error_msg = _check_config()
    if not is_configured:
        return {"success": False, "error": error_msg}

    # Get client lazily
    notion = _get_notion_client()

    # Extract page ID from URL if needed
    if "notion.so" in page_id:
        page_id = page_id.split("/")[-1].split("?")[0]

    try:
        response = notion.pages.update(page_id=page_id, archived=True)

        return {
            "success": True,
            "page_id": response["id"],
            "archived": response["archived"],
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def register_tools(mcp):
    """
    Register all Notion tools with the main FastMCP server.
    Only registers tools if Notion is properly configured.
    """
    is_configured, error_msg = _check_config()
    if not is_configured:
        print(f"⚠ Notion tools not registered: {error_msg}", file=sys.stderr)
        return False

    # Register each tool
    mcp.add_tool(create_database_page)
    mcp.add_tool(get_database)
    mcp.add_tool(get_page)
    mcp.add_tool(update_page)
    mcp.add_tool(create_page)
    mcp.add_tool(archive_page)

    return True
