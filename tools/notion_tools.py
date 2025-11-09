"""
Notion MCP Tools - CRUD operations for Notion workspaces
"""

import json
import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from notion_client import Client

# Load environment variables
load_dotenv()

# Initialize Notion client
notion_token = os.getenv("NOTION_TOKEN")
if not notion_token:
    raise ValueError(
        "NOTION_TOKEN environment variable is not set. Get one from https://www.notion.so/my-integrations"
    )

notion = Client(auth=notion_token)
router = FastMCP("notion-tools")

DEFAULT_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")


@router.tool()
def create_database_page(
    title: str,
    database_id: Optional[str] = None,
    properties: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create a new page in a Notion database.

    Args:
        title: The title of the page
        database_id: The ID of the database (uses NOTION_DATABASE_ID from env if not provided)
        properties: Additional properties to set on the page (as a JSON string or dict)

    Returns:
        The created page object
    """
    db_id = database_id or DEFAULT_DATABASE_ID
    if not db_id:
        raise ValueError(
            "No database_id provided and NOTION_DATABASE_ID environment variable is not set"
        )

    # Prepare the page properties
    page_properties = {"title": {"title": [{"text": {"content": title}}]}}

    # Add additional properties if provided
    if properties:
        if isinstance(properties, str):
            try:
                properties = json.loads(properties)
            except json.JSONDecodeError:
                raise ValueError("Properties must be valid JSON string or a dictionary")

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


@router.tool()
def get_database(
    database_id: Optional[str] = None,
    filter_json: Optional[str] = None,
    sorts: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Query a Notion database and return pages.

    Args:
        database_id: The ID of the database (uses NOTION_DATABASE_ID from env if not provided)
        filter_json: JSON string for filtering results (Notion API filter format)
        sorts: List of sort objects, e.g., [{"property": "Name", "direction": "ascending"}]

    Returns:
        List of pages in the database
    """
    db_id = database_id or DEFAULT_DATABASE_ID
    if not db_id:
        raise ValueError(
            "No database_id provided and NOTION_DATABASE_ID environment variable is not set"
        )

    query_params = {}

    if filter_json:
        try:
            query_params["filter"] = json.loads(filter_json)
        except json.JSONDecodeError:
            raise ValueError("filter_json must be a valid JSON string")

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


@router.tool()
def get_page(page_id: str) -> Dict[str, Any]:
    """
    Get a Notion page by ID and its content.

    Args:
        page_id: The ID of the page (can be full URL or just the ID)

    Returns:
        The page object with content
    """
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


@router.tool()
def update_page(page_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update properties of a Notion page.

    Args:
        page_id: The ID of the page to update
        properties: Properties to update (as JSON string or dict)

    Returns:
        The updated page object
    """
    # Extract page ID from URL if needed
    if "notion.so" in page_id:
        page_id = page_id.split("/")[-1].split("?")[0]

    # Parse properties if they're a JSON string
    if isinstance(properties, str):
        try:
            properties = json.loads(properties)
        except json.JSONDecodeError:
            raise ValueError("Properties must be valid JSON string or a dictionary")

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


@router.tool()
def create_page(
    title: str, parent_page_id: Optional[str] = None, content: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a standalone Notion page (not in a database).

    Args:
        title: The title of the page
        parent_page_id: Optional parent page ID (if not provided, creates in root)
        content: Optional markdown-like content to add to the page

    Returns:
        The created page object
    """
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


@router.tool()
def archive_page(page_id: str) -> Dict[str, Any]:
    """
    Archive (delete) a Notion page.

    Args:
        page_id: The ID of the page to archive

    Returns:
        Success status
    """
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
