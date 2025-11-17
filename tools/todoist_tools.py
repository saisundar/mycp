"""
Todoist MCP Tools - Task management operations for Todoist
Optimized for FastMCP Cloud deployment with completely lazy loading
"""

import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from todoist_api_python.api import TodoistAPI

# Lazy loading state - don't load anything at import time
_todoist_token = None
_api_client = None
_env_loaded = False


def _load_env():
    """Load environment variables on first access."""
    global _todoist_token, _env_loaded
    if not _env_loaded:
        load_dotenv()
        _todoist_token = os.getenv("TODOIST_TOKEN")
        _env_loaded = True


def _get_api_client() -> TodoistAPI:
    """
    Get or create Todoist API client lazily.
    Only initializes when first tool is called.
    """
    global _api_client
    if _api_client is None:
        _load_env()
        if not _todoist_token:
            raise ValueError(
                "TODOIST_TOKEN environment variable is not set. Get one from https://todoist.com/app/settings/integrations"
            )
        _api_client = TodoistAPI(_todoist_token)
    return _api_client


def _check_config() -> tuple[bool, str]:
    """
    Check if Todoist is properly configured and return status + message.
    This now also verifies the client can be initialized.
    """
    _load_env()

    if not _todoist_token:
        return (
            False,
            "TODOIST_TOKEN environment variable is not set. Get one from https://todoist.com/app/settings/integrations",
        )

    # Try to get client to verify it's valid
    try:
        _get_api_client()
    except Exception as e:
        return False, f"Failed to initialize Todoist client: {e}"

    return True, ""


def create_task(
    content: str,
    description: Optional[str] = None,
    project_id: Optional[str] = None,
    section_id: Optional[str] = None,
    parent_id: Optional[str] = None,
    order: Optional[int] = None,
    labels: Optional[List[str]] = None,
    priority: Optional[int] = None,
    due_string: Optional[str] = None,
    due_date: Optional[str] = None,
    due_datetime: Optional[str] = None,
    due_lang: Optional[str] = None,
    assignee_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a new task in Todoist.
    """
    # Check configuration at runtime
    is_configured, error_msg = _check_config()
    if not is_configured:
        return {"success": False, "error": error_msg}

    # Get client lazily
    api = _get_api_client()

    try:
        task = api.add_task(
            content=content,
            description=description,
            project_id=project_id,
            section_id=section_id,
            parent_id=parent_id,
            order=order,
            labels=labels,
            priority=priority,
            due_string=due_string,
            due_date=due_date,
            due_datetime=due_datetime,
            due_lang=due_lang,
            assignee_id=assignee_id,
        )

        return {
            "success": True,
            "task": {
                "id": task.id,
                "content": task.content,
                "description": task.description,
                "project_id": task.project_id,
                "section_id": task.section_id,
                "parent_id": task.parent_id,
                "order": task.order,
                "labels": task.labels,
                "priority": task.priority,
                "due": task.due.to_dict() if task.due else None,
                "url": task.url,
                "comment_count": task.comment_count,
                "completed": task.is_completed,
                "created_at": task.created_at.isoformat() if task.created_at else None,
            },
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_tasks(
    project_id: Optional[str] = None,
    section_id: Optional[str] = None,
    label: Optional[str] = None,
    filter_query: Optional[str] = None,
    lang: Optional[str] = None,
    ids: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Get tasks from Todoist.
    """
    is_configured, error_msg = _check_config()
    if not is_configured:
        return {"success": False, "error": error_msg}

    # Get client lazily
    api = _get_api_client()

    try:
        tasks = api.get_tasks(
            project_id=project_id,
            section_id=section_id,
            label=label,
            filter=filter_query,
            lang=lang,
            ids=ids,
        )

        task_list = []
        for task in tasks:
            task_list.append(
                {
                    "id": task.id,
                    "content": task.content,
                    "description": task.description,
                    "project_id": task.project_id,
                    "section_id": task.section_id,
                    "parent_id": task.parent_id,
                    "order": task.order,
                    "labels": task.labels,
                    "priority": task.priority,
                    "due": task.due.to_dict() if task.due else None,
                    "url": task.url,
                    "comment_count": task.comment_count,
                    "completed": task.is_completed,
                    "created_at": task.created_at.isoformat()
                    if task.created_at
                    else None,
                }
            )

        return {
            "success": True,
            "tasks": task_list,
            "count": len(task_list),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def complete_task(task_id: str) -> Dict[str, Any]:
    """
    Mark a task as completed.
    """
    is_configured, error_msg = _check_config()
    if not is_configured:
        return {"success": False, "error": error_msg}

    # Get client lazily
    api = _get_api_client()

    try:
        is_success = api.close_task(task_id=task_id)

        return {
            "success": is_success,
            "task_id": task_id,
            "completed": True,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def update_task(
    task_id: str,
    content: Optional[str] = None,
    description: Optional[str] = None,
    labels: Optional[List[str]] = None,
    priority: Optional[int] = None,
    due_string: Optional[str] = None,
    due_date: Optional[str] = None,
    due_datetime: Optional[str] = None,
    due_lang: Optional[str] = None,
    assignee_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Update an existing task in Todoist.
    """
    is_configured, error_msg = _check_config()
    if not is_configured:
        return {"success": False, "error": error_msg}

    # Get client lazily
    api = _get_api_client()

    try:
        task = api.update_task(
            task_id=task_id,
            content=content,
            description=description,
            labels=labels,
            priority=priority,
            due_string=due_string,
            due_date=due_date,
            due_datetime=due_datetime,
            due_lang=due_lang,
            assignee_id=assignee_id,
        )

        return {
            "success": True,
            "task": {
                "id": task.id,
                "content": task.content,
                "description": task.description,
                "project_id": task.project_id,
                "section_id": task.section_id,
                "parent_id": task.parent_id,
                "order": task.order,
                "labels": task.labels,
                "priority": task.priority,
                "due": task.due.to_dict() if task.due else None,
                "url": task.url,
                "comment_count": task.comment_count,
                "completed": task.is_completed,
                "created_at": task.created_at.isoformat() if task.created_at else None,
            },
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def delete_task(task_id: str) -> Dict[str, Any]:
    """
    Delete a task from Todoist.
    """
    is_configured, error_msg = _check_config()
    if not is_configured:
        return {"success": False, "error": error_msg}

    # Get client lazily
    api = _get_api_client()

    try:
        is_success = api.delete_task(task_id=task_id)

        return {
            "success": is_success,
            "task_id": task_id,
            "deleted": True,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_projects() -> Dict[str, Any]:
    """
    Get all projects from Todoist.
    """
    is_configured, error_msg = _check_config()
    if not is_configured:
        return {"success": False, "error": error_msg}

    # Get client lazily
    api = _get_api_client()

    try:
        projects = api.get_projects()

        project_list = []
        for project in projects:
            project_list.append(
                {
                    "id": project.id,
                    "name": project.name,
                    "color": project.color,
                    "parent_id": project.parent_id,
                    "order": project.order,
                    "comment_count": project.comment_count,
                    "is_shared": project.is_shared,
                    "is_favorite": project.is_favorite,
                    "url": project.url,
                    "is_inbox_project": project.is_inbox_project,
                    "is_team_inbox": project.is_team_inbox,
                }
            )

        return {
            "success": True,
            "projects": project_list,
            "count": len(project_list),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def reopen_task(task_id: str) -> Dict[str, Any]:
    """
    Reopen a completed task.
    """
    is_configured, error_msg = _check_config()
    if not is_configured:
        return {"success": False, "error": error_msg}

    # Get client lazily
    api = _get_api_client()

    try:
        is_success = api.reopen_task(task_id=task_id)

        return {
            "success": is_success,
            "task_id": task_id,
            "completed": False,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_task(task_id: str) -> Dict[str, Any]:
    """
    Get a specific task by ID.
    """
    is_configured, error_msg = _check_config()
    if not is_configured:
        return {"success": False, "error": error_msg}

    # Get client lazily
    api = _get_api_client()

    try:
        task = api.get_task(task_id=task_id)

        return {
            "success": True,
            "task": {
                "id": task.id,
                "content": task.content,
                "description": task.description,
                "project_id": task.project_id,
                "section_id": task.section_id,
                "parent_id": task.parent_id,
                "order": task.order,
                "labels": task.labels,
                "priority": task.priority,
                "due": task.due.to_dict() if task.due else None,
                "url": task.url,
                "comment_count": task.comment_count,
                "completed": task.is_completed,
                "created_at": task.created_at.isoformat() if task.created_at else None,
            },
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def register_tools(mcp):
    """
    Register all Todoist tools with the main FastMCP server.
    Only registers tools if Todoist is properly configured.
    """
    is_configured, error_msg = _check_config()
    if not is_configured:
        print(f"⚠ Todoist tools not registered: {error_msg}")
        return False

    # Register each tool
    mcp.tool(create_task)
    mcp.tool(get_tasks)
    mcp.tool(complete_task)
    mcp.tool(update_task)
    mcp.tool(delete_task)
    mcp.tool(get_projects)
    mcp.tool(reopen_task)
    mcp.tool(get_task)

    return True
