"""
Obsidian MCP Tools - Note management operations for Obsidian vaults
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Obsidian configuration (without raising errors at import time)
OBSIDIAN_VAULT_PATH = os.getenv("OBSIDIAN_VAULT_PATH")
OBSIDIAN_TEMPLATES_PATH = os.getenv("OBSIDIAN_TEMPLATES_PATH", "templates/")

# Vault path validation will happen at runtime
vault_path = None
if OBSIDIAN_VAULT_PATH:
    vault_path = Path(OBSIDIAN_VAULT_PATH)
    if not vault_path.exists():
        # Don't raise error at import time, just mark as invalid
        vault_path = None


def _check_config() -> tuple[bool, str]:
    """Check if Obsidian is properly configured and return status + message."""
    if not OBSIDIAN_VAULT_PATH:
        return False, "OBSIDIAN_VAULT_PATH environment variable is not set"

    path = Path(OBSIDIAN_VAULT_PATH)
    if not path.exists():
        return False, f"Obsidian vault path does not exist: {OBSIDIAN_VAULT_PATH}"

    return True, ""


def _get_note_path(note_name: str) -> Path:
    """Get the full path for a note, handling .md extension."""
    if not OBSIDIAN_VAULT_PATH:
        raise ValueError("OBSIDIAN_VAULT_PATH environment variable is not set")

    vault = Path(OBSIDIAN_VAULT_PATH)
    if not note_name.endswith(".md"):
        note_name += ".md"
    return vault / note_name


def _ensure_directory_exists(file_path: Path) -> None:
    """Ensure the parent directory exists for a file."""
    file_path.parent.mkdir(parents=True, exist_ok=True)


def read_note(note_path: str) -> Dict[str, Any]:
    """
    Read the content of an Obsidian note.

    Args:
        note_path: Path to the note relative to vault root (e.g., "folder/note" or "folder/note.md")

    Returns:
        Note content and metadata
    """
    # Check configuration first
    is_configured, error_msg = _check_config()
    if not is_configured:
        return {
            "success": False,
            "error": error_msg,
        }

    try:
        full_path = _get_note_path(note_path)

        if not full_path.exists():
            return {
                "success": False,
                "error": f"Note not found: {note_path}",
            }

        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Get file stats
        stat = full_path.stat()

        return {
            "success": True,
            "note": {
                "path": str(full_path.relative_to(Path(OBSIDIAN_VAULT_PATH))),
                "content": content,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            },
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_note(
    note_path: str,
    content: str,
    overwrite: bool = False,
    frontmatter: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create a new Obsidian note.

    Args:
        note_path: Path for the new note relative to vault root (e.g., "folder/note" or "folder/note.md")
        content: Content of the note
        overwrite: Whether to overwrite if note already exists
        frontmatter: Optional frontmatter to add as YAML

    Returns:
        Success status and note metadata
    """
    # Check configuration first
    is_configured, error_msg = _check_config()
    if not is_configured:
        return {
            "success": False,
            "error": error_msg,
        }

    try:
        full_path = _get_note_path(note_path)

        # Check if file already exists
        if full_path.exists() and not overwrite:
            return {
                "success": False,
                "error": f"Note already exists: {note_path}. Use overwrite=True to replace it.",
            }

        # Ensure directory exists
        _ensure_directory_exists(full_path)

        # Prepare content with frontmatter if provided
        final_content = ""
        if frontmatter:
            final_content += "---\n"
            for key, value in frontmatter.items():
                final_content += f"{key}: {value}\n"
            final_content += "---\n\n"

        final_content += content

        # Write the file
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(final_content)

        # Get file stats
        stat = full_path.stat()

        return {
            "success": True,
            "note": {
                "path": str(full_path.relative_to(Path(OBSIDIAN_VAULT_PATH))),
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            },
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def update_note(note_path: str, content: str) -> Dict[str, Any]:
    """
    Completely replace the content of an existing Obsidian note.

    Args:
        note_path: Path to the note relative to vault root
        content: New content to replace the entire note

    Returns:
        Success status and note metadata
    """
    # Check configuration first
    is_configured, error_msg = _check_config()
    if not is_configured:
        return {
            "success": False,
            "error": error_msg,
        }

    try:
        full_path = _get_note_path(note_path)

        if not full_path.exists():
            return {
                "success": False,
                "error": f"Note not found: {note_path}",
            }

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Get file stats
        stat = full_path.stat()

        return {
            "success": True,
            "note": {
                "path": str(full_path.relative_to(Path(OBSIDIAN_VAULT_PATH))),
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            },
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def append_to_note(
    note_path: str, content: str, add_newline: bool = True
) -> Dict[str, Any]:
    """
    Append content to the end of an existing Obsidian note.

    Args:
        note_path: Path to the note relative to vault root
        content: Content to append
        add_newline: Whether to add a newline before appending

    Returns:
        Success status and note metadata
    """
    # Check configuration first
    is_configured, error_msg = _check_config()
    if not is_configured:
        return {
            "success": False,
            "error": error_msg,
        }

    try:
        full_path = _get_note_path(note_path)

        if not full_path.exists():
            return {
                "success": False,
                "error": f"Note not found: {note_path}",
            }

        with open(full_path, "a", encoding="utf-8") as f:
            if add_newline:
                f.write("\n")
            f.write(content)

        # Get file stats
        stat = full_path.stat()

        return {
            "success": True,
            "note": {
                "path": str(full_path.relative_to(Path(OBSIDIAN_VAULT_PATH))),
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            },
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_notes(folder: str = "") -> Dict[str, Any]:
    """
    List all notes in a folder (or entire vault).

    Args:
        folder: Folder path relative to vault root (empty string for root)

    Returns:
        List of notes with metadata
    """
    # Check configuration first
    is_configured, error_msg = _check_config()
    if not is_configured:
        return {
            "success": False,
            "error": error_msg,
        }

    try:
        vault = Path(OBSIDIAN_VAULT_PATH)
        search_path = vault / folder if folder else vault

        if not search_path.exists():
            return {
                "success": False,
                "error": f"Folder not found: {folder}",
            }

        notes = []
        for md_file in search_path.rglob("*.md"):
            try:
                rel_path = str(md_file.relative_to(vault))
                stat = md_file.stat()

                notes.append(
                    {
                        "path": rel_path,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    }
                )
            except Exception:
                continue

        return {
            "success": True,
            "notes": sorted(notes, key=lambda x: x["path"]),
            "count": len(notes),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def search_notes(query: str, case_sensitive: bool = False) -> Dict[str, Any]:
    """
    Search for notes containing specific text.

    Args:
        query: Text to search for
        case_sensitive: Whether search should be case sensitive

    Returns:
        List of matching notes with context
    """
    # Check configuration first
    is_configured, error_msg = _check_config()
    if not is_configured:
        return {
            "success": False,
            "error": error_msg,
        }

    try:
        vault = Path(OBSIDIAN_VAULT_PATH)
        matching_notes = []

        for md_file in vault.rglob("*.md"):
            try:
                with open(md_file, "r", encoding="utf-8") as f:
                    content = f.read()

                search_content = content if case_sensitive else content.lower()
                search_query = query if case_sensitive else query.lower()

                if search_query in search_content:
                    # Find line numbers with matches
                    lines = content.split("\n")
                    matches = []

                    for i, line in enumerate(lines, 1):
                        search_line = line if case_sensitive else line.lower()
                        if search_query in search_line:
                            matches.append(
                                {
                                    "line": i,
                                    "content": line[:200],  # Truncate long lines
                                }
                            )

                    rel_path = str(md_file.relative_to(vault))
                    stat = md_file.stat()

                    matching_notes.append(
                        {
                            "path": rel_path,
                            "matches": matches,
                            "match_count": len(matches),
                            "size": stat.st_size,
                            "modified": datetime.fromtimestamp(
                                stat.st_mtime
                            ).isoformat(),
                        }
                    )
            except Exception:
                continue

        return {
            "success": True,
            "query": query,
            "notes": sorted(
                matching_notes, key=lambda x: x["match_count"], reverse=True
            ),
            "count": len(matching_notes),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def delete_note(note_path: str) -> Dict[str, Any]:
    """
    Delete an Obsidian note (moves to trash if possible, otherwise permanent delete).

    Args:
        note_path: Path to the note relative to vault root

    Returns:
        Success status
    """
    # Check configuration first
    is_configured, error_msg = _check_config()
    if not is_configured:
        return {
            "success": False,
            "error": error_msg,
        }

    try:
        full_path = _get_note_path(note_path)

        if not full_path.exists():
            return {
                "success": False,
                "error": f"Note not found: {note_path}",
            }

        # Try to move to trash first (more OS-agnostic)
        import shutil

        try:
            shutil.move(str(full_path), str(full_path) + ".trash")
            deleted_path = str(full_path) + ".trash"
        except:
            # If trash fails, just delete
            full_path.unlink()
            deleted_path = str(full_path)

        return {
            "success": True,
            "deleted_path": deleted_path,
            "permanent": not deleted_path.endswith(".trash"),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_note_metadata(note_path: str) -> Dict[str, Any]:
    """
    Get metadata for a note without reading its full content.

    Args:
        note_path: Path to the note relative to vault root

    Returns:
        Note metadata including word count, line count, etc.
    """
    # Check configuration first
    is_configured, error_msg = _check_config()
    if not is_configured:
        return {
            "success": False,
            "error": error_msg,
        }

    try:
        full_path = _get_note_path(note_path)

        if not full_path.exists():
            return {
                "success": False,
                "error": f"Note not found: {note_path}",
            }

        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()

        stat = full_path.stat()

        # Count words and lines
        words = len(content.split())
        lines = len(content.split("\n"))

        # Check for frontmatter
        has_frontmatter = content.startswith("---\n")

        return {
            "success": True,
            "metadata": {
                "path": str(full_path.relative_to(Path(OBSIDIAN_VAULT_PATH))),
                "size_bytes": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "word_count": words,
                "line_count": lines,
                "has_frontmatter": has_frontmatter,
            },
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def register_tools(mcp):
    """
    Register all Obsidian tools with the main FastMCP server.
    Only registers tools if Obsidian is properly configured.
    """
    is_configured, error_msg = _check_config()
    if not is_configured:
        print(f"⚠ Obsidian tools not registered: {error_msg}", file=sys.stderr)
        return False

    # Register each tool
    mcp.add_tool(read_note)
    mcp.add_tool(create_note)
    mcp.add_tool(update_note)
    mcp.add_tool(append_to_note)
    mcp.add_tool(list_notes)
    mcp.add_tool(search_notes)
    mcp.add_tool(delete_note)
    mcp.add_tool(get_note_metadata)

    return True
