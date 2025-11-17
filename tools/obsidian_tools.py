"""
Obsidian MCP Tools - Note management operations for Obsidian vaults
Optimized for FastMCP Cloud deployment with completely lazy loading
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

# Lazy loading state - don't load anything at import time
_OBSIDIAN_VAULT_PATH = None
_OBSIDIAN_TEMPLATES_PATH = None
_env_loaded = False
_vault_path = None


def _load_env():
    """Load environment variables on first access."""
    global _OBSIDIAN_VAULT_PATH, _OBSIDIAN_TEMPLATES_PATH, _env_loaded
    if not _env_loaded:
        load_dotenv()
        _OBSIDIAN_VAULT_PATH = os.getenv("OBSIDIAN_VAULT_PATH")
        _OBSIDIAN_TEMPLATES_PATH = os.getenv("OBSIDIAN_TEMPLATES_PATH", "templates/")
        _env_loaded = True


def _get_vault_path() -> Path:
    """Get vault path, loading env if needed."""
    _load_env()
    if not _OBSIDIAN_VAULT_PATH:
        raise ValueError("OBSIDIAN_VAULT_PATH environment variable is not set")
    return Path(_OBSIDIAN_VAULT_PATH)


def _check_config() -> tuple[bool, str]:
    """Check if Obsidian is properly configured and return status + message."""
    _load_env()

    if not _OBSIDIAN_VAULT_PATH:
        return False, "OBSIDIAN_VAULT_PATH environment variable is not set"

    path = Path(_OBSIDIAN_VAULT_PATH)
    if not path.exists():
        return False, f"Obsidian vault path does not exist: {_OBSIDIAN_VAULT_PATH}"

    return True, ""


def _get_note_path(note_name: str) -> Path:
    """Get the full path for a note, handling .md extension."""
    vault_path = _get_vault_path()
    if not note_name.endswith(".md"):
        note_name += ".md"
    return vault_path / note_name


def _ensure_directory_exists(file_path: Path) -> None:
    """Ensure the parent directory exists for a file."""
    file_path.parent.mkdir(parents=True, exist_ok=True)


def read_note(note_path: str) -> Dict[str, Any]:
    """Read the content of an Obsidian note."""
    is_configured, error_msg = _check_config()
    if not is_configured:
        return {"success": False, "error": error_msg}

    try:
        full_path = _get_note_path(note_path)

        if not full_path.exists():
            return {"success": False, "error": f"Note not found: {note_path}"}

        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()

        stat = full_path.stat()
        vault_path = _get_vault_path()

        return {
            "success": True,
            "note": {
                "path": str(full_path.relative_to(vault_path)),
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
    """Create a new Obsidian note."""
    is_configured, error_msg = _check_config()
    if not is_configured:
        return {"success": False, "error": error_msg}

    try:
        full_path = _get_note_path(note_path)

        if full_path.exists() and not overwrite:
            return {
                "success": False,
                "error": f"Note already exists: {note_path}. Use overwrite=True to replace it.",
            }

        _ensure_directory_exists(full_path)

        final_content = ""
        if frontmatter:
            final_content += "---\n"
            for key, value in frontmatter.items():
                final_content += f"{key}: {value}\n"
            final_content += "---\n\n"

        final_content += content

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(final_content)

        stat = full_path.stat()
        vault_path = _get_vault_path()

        return {
            "success": True,
            "note": {
                "path": str(full_path.relative_to(vault_path)),
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            },
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def update_note(note_path: str, content: str) -> Dict[str, Any]:
    """Completely replace the content of an existing Obsidian note."""
    is_configured, error_msg = _check_config()
    if not is_configured:
        return {"success": False, "error": error_msg}

    try:
        full_path = _get_note_path(note_path)

        if not full_path.exists():
            return {"success": False, "error": f"Note not found: {note_path}"}

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

        stat = full_path.stat()
        vault_path = _get_vault_path()

        return {
            "success": True,
            "note": {
                "path": str(full_path.relative_to(vault_path)),
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            },
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def append_to_note(
    note_path: str, content: str, add_newline: bool = True
) -> Dict[str, Any]:
    """Append content to the end of an existing Obsidian note."""
    is_configured, error_msg = _check_config()
    if not is_configured:
        return {"success": False, "error": error_msg}

    try:
        full_path = _get_note_path(note_path)

        if not full_path.exists():
            return {"success": False, "error": f"Note not found: {note_path}"}

        with open(full_path, "a", encoding="utf-8") as f:
            if add_newline:
                f.write("\n")
            f.write(content)

        stat = full_path.stat()
        vault_path = _get_vault_path()

        return {
            "success": True,
            "note": {
                "path": str(full_path.relative_to(vault_path)),
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            },
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_notes(folder: str = "") -> Dict[str, Any]:
    """List all notes in a folder (or entire vault)."""
    is_configured, error_msg = _check_config()
    if not is_configured:
        return {"success": False, "error": error_msg}

    try:
        vault_path = _get_vault_path()
        search_path = vault_path / folder if folder else vault_path

        if not search_path.exists():
            return {"success": False, "error": f"Folder not found: {folder}"}

        notes = []
        for md_file in search_path.rglob("*.md"):
            try:
                rel_path = str(md_file.relative_to(vault_path))
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
    """Search for notes containing specific text."""
    is_configured, error_msg = _check_config()
    if not is_configured:
        return {"success": False, "error": error_msg}

    try:
        vault_path = _get_vault_path()
        matching_notes = []

        for md_file in vault_path.rglob("*.md"):
            try:
                with open(md_file, "r", encoding="utf-8") as f:
                    content = f.read()

                search_content = content if case_sensitive else content.lower()
                search_query = query if case_sensitive else query.lower()

                if search_query in search_content:
                    lines = content.split("\n")
                    matches = []

                    for i, line in enumerate(lines, 1):
                        search_line = line if case_sensitive else line.lower()
                        if search_query in search_line:
                            matches.append(
                                {
                                    "line": i,
                                    "content": line[:200],
                                }
                            )

                    rel_path = str(md_file.relative_to(vault_path))
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
    """Delete an Obsidian note."""
    is_configured, error_msg = _check_config()
    if not is_configured:
        return {"success": False, "error": error_msg}

    try:
        full_path = _get_note_path(note_path)

        if not full_path.exists():
            return {"success": False, "error": f"Note not found: {note_path}"}

        import shutil

        try:
            shutil.move(str(full_path), str(full_path) + ".trash")
            deleted_path = str(full_path) + ".trash"
        except:
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
    """Get metadata for a note without reading its full content."""
    is_configured, error_msg = _check_config()
    if not is_configured:
        return {"success": False, "error": error_msg}

    try:
        full_path = _get_note_path(note_path)

        if not full_path.exists():
            return {"success": False, "error": f"Note not found: {note_path}"}

        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()

        stat = full_path.stat()
        vault_path = _get_vault_path()

        words = len(content.split())
        lines = len(content.split("\n"))
        has_frontmatter = content.startswith("---\n")

        return {
            "success": True,
            "metadata": {
                "path": str(full_path.relative_to(vault_path)),
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
    """Register all Obsidian tools with the main FastMCP server."""
    is_configured, error_msg = _check_config()
    if not is_configured:
        print(f"⚠ Obsidian tools not registered: {error_msg}")
        return False

    mcp.tool(read_note)
    mcp.tool(create_note)
    mcp.tool(update_note)
    mcp.tool(append_to_note)
    mcp.tool(list_notes)
    mcp.tool(search_notes)
    mcp.tool(delete_note)
    mcp.tool(get_note_metadata)

    return True
