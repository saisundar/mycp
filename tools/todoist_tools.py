"""
Todoist MCP Tools - Task management operations for Todoist
"""

import os
from typing import Dict, List, Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from todoist_api_python.api import TodoistAPI

# Load environment variables
load_dotenv()

# Initialize Todoist client
todoist_token = os.getenv("TODOIST_TOKEN")
if not todoist_token:
    raise ValueError(
        "TODOIST_TOKEN environment variable is not set. Get one from https://todoist.com/app/settings/integrations"
    )

api = TodoistAPI(todoist_token)
router = FastMCP("todoist-tools")


@router.tool()
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

    Args:
        content: Task content (required)
        description: Task description
        project_id: Project ID (use get_projects to find available projects)
        section_id: Section ID
        parent_id: Parent task ID (for sub-tasks)
        order: Task order
        labels: List of label names
        priority: Task priority (1-4, where 4 is highest)
        due_string: Human-readable due date (e.g., "tomorrow at 12:00", "every day")
        due_date: Specific due date in YYYY-MM-DD format
        due_datetime: Specific due datetime in RFC3339 format
        due_lang: Language for due_string (e.g., "en", "es")
        assignee_id: Assignee ID (for shared projects)

    Returns:
        Created task object
    """
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


@router.tool()
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

    Args:
        project_id: Filter by project ID
        section_id: Filter by section ID
        label: Filter by label
        filter_query: Filter using Todoist's natural language (e.g., "today", "p1", "@home")
        lang: Language for filter_query
        ids: Specific task IDs to retrieve

    Returns:
        List of tasks
    """
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


@router.tool()
def complete_task(task_id: str) -> Dict[str, Any]:
    """
    Mark a task as completed.

    Args:
        task_id: The ID of the task to complete

    Returns:
        Success status
    """
    try:
        is_success = api.close_task(task_id=task_id)

        return {
            "success": is_success,
            "task_id": task_id,
            "completed": True,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.tool()
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

    Args:
        task_id: The ID of the task to update
        content: New task content
        description: New task description
        labels: New list of label names
        priority: New priority (1-4, where 4 is highest)
        due_string: New human-readable due date
        due_date: New specific due date in YYYY-MM-DD format
        due_datetime: New specific due datetime in RFC3339 format
        due_lang: Language for due_string
        assignee_id: New assignee ID

    Returns:
        Updated task object
    """
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


@router.tool()
def delete_task(task_id: str) -> Dict[str, Any]:
    """
    Delete a task from Todoist.

    Args:
        task_id: The ID of the task to delete

    Returns:
        Success status
    """
    try:
        is_success = api.delete_task(task_id=task_id)

        return {
            "success": is_success,
            "task_id": task_id,
            "deleted": True,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.tool()
def get_projects() -> Dict[str, Any]:
    """
    Get all projects from Todoist.

    Returns:
        List of projects
    """
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


@router.tool()
def reopen_task(task_id: str) -> Dict[str, Any]:
    """
    Reopen a completed task.

    Args:
        task_id: The ID of the task to reopen

    Returns:
        Success status
    """
    try:
        is_success = api.reopen_task(task_id=task_id)

        return {
            "success": is_success,
            "task_id": task_id,
            "completed": False,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.tool()
def get_task(task_id: str) -> Dict[str, Any]:
    """
    Get a specific task by ID.

    Args:
        task_id: The ID of the task to retrieve

    Returns:
        Task object
    """
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
